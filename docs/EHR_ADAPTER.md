<div align="center">

# 🔌 Writing an EHR / HBYS Adapter

_How to connect CerebraLink to **your** Electronic Health Record system._

</div>

---

> [!IMPORTANT]
> The reference adapter that ships in this repo was built for **Acıbadem
> CerebralPlus** (a Turkish HBYS). The institution-specific scraping scripts
> (`scripts/cerebral_*.py`) — which contain real endpoints, HTML selectors, and
> cookie-auth logic — are **intentionally NOT distributed**. They are kept local
> via `.gitignore`. This guide shows you how to write a clean adapter for any EHR
> (FHIR, Epic, Cerner, OpenEMR, a CSV export, a research data warehouse…) without
> ever needing them.

This adapter layer is what makes CerebraLink **FHIR R4 and HL7 v2 compatible**: map
FHIR resources (`Patient`, `Encounter`, `DiagnosticReport`, …) or HL7 v2 segments
(`PID`, `PV1`, `OBX`, …) into the normalized patient dict shown below, and every
downstream component — PHI masking, RAG, the graph, the agents — works unchanged.
Compatibility lives entirely in this one function; you map your source once.

## 📑 Contents

- [🧠 How CerebraLink consumes patient data](#-how-cerebralink-consumes-patient-data)
- [📜 The Adapter Contract](#-the-adapter-contract)
- [🧾 The Patient Data Shape](#-the-patient-data-shape)
- [🛠️ Step-by-step: build your adapter](#️-step-by-step-build-your-adapter)
- [🔥 Example A — FHIR R4 adapter](#-example-a--fhir-r4-adapter)
- [📁 Example B — Local file / CSV export](#-example-b--local-file--csv-export)
- [🔐 Authentication patterns](#-authentication-patterns)
- [🧪 How lab reports are parsed](#-how-lab-reports-are-parsed)
- [🗃️ Caching & performance](#️-caching--performance)
- [✅ Compliance checklist](#-compliance-checklist)

## 🧠 How CerebraLink consumes patient data

When a clinician's message contains a patient/protocol identifier, the
orchestrator (`core/orchestrator.py`) calls a single entry point:

```python
from src.backend.tools.ehr import auto_fetch_patient   # adapter chosen by EHR_ADAPTER

raw_patient = await auto_fetch_patient(detected_pid)   # ← your adapter
masked      = await self.phi_checker.mask_patient_record(raw_patient)  # PHI mask
# … masked context is then fed to the council agents
```

So **all you have to provide is one async function** that takes an identifier and
returns a patient dict. Everything downstream — PHI masking, RAG indexing, graph
ingestion, the agents — is EHR-agnostic.

```
your EHR  ──►  auto_fetch_patient(id)  ──►  {patient dict}  ──►  🛡️ PHI Masker  ──►  🧠 agents
              └────────── adapter ──────────┘
```

> [!NOTE]
> **Which adapter is active** is set by the `EHR_ADAPTER` env var, read in
> `core/config.py` and dispatched by `tools/ehr.py`:
> - `file` *(default)* → `tools/file_adapter.py` — loads a synthetic/local
>   `patient_<id>.json`. **Runs on a fresh clone**; ships with
>   `examples/patient_DEMO.json` (query the id `DEMO`).
> - `cerebral` → `tools/cerebral.py` — Acıbadem CerebralPlus. **Does not run on a
>   fresh clone**: it wraps the git-ignored `scripts/cerebral_*.py` scrapers and
>   needs `cookies/cookies.json`.

## 📜 The Adapter Contract

Implement these in your own module — copy `src/backend/tools/file_adapter.py` (the
shipped default) as a starting point, then select it with `EHR_ADAPTER` (don't edit
`cerebral.py`; it is the Acıbadem-specific adapter and needs the git-ignored
scrapers). Only `auto_fetch_patient` is strictly required; the others enable
caching and file import.

```python
async def auto_fetch_patient(protocol_id: str) -> dict[str, Any]:
    """REQUIRED. Resolve an identifier to a normalized patient dict.
       Should use a local cache when available, then hit the EHR."""

def patient_exists(protocol_id: str) -> bool:
    """Optional. True if patient data is already cached locally."""

def load_cached_patient(protocol_id: str) -> dict[str, Any]:
    """Optional. Load a cached patient dict from disk."""

async def fetch_patient(patient_id: str, auth: str) -> dict[str, Any]:
    """Optional. The raw fetch (network call) behind auto_fetch_patient."""

async def load_patient_from_file(path: str) -> dict[str, Any]:
    """Optional. Load an already-exported patient JSON file."""
```

### Identifier normalization
The reference adapter strips spaces/dashes so `"7352 4705"` and `"73524705"` both
resolve. Mirror this in your adapter:

```python
import re
def _normalize_protocol_id(pid: str) -> str:
    return re.sub(r"[\s\-]+", "", pid.strip())
```

## 🧾 The Patient Data Shape

`auto_fetch_patient` must return a JSON-serializable dict. The richer it is, the
more the agents can do — but only a few keys are needed to get value. Minimal:

```jsonc
{
  "patient": {
    "full_name": "SYNTHETIC, Patient",   // masked later; synthetic for tests
    "age": 64,
    "sex": "F",
    "mrn": "REDACTED"
  },
  "episodes": [                            // visits / admissions
    {
      "episode_id": "E-001",
      "date": "2026-03-01",
      "service": "Cardiology",
      "examination_text": "Chest pain on exertion; ECG sinus rhythm…",
      "diagnoses": [{"code": "I20.9", "label": "Angina pectoris"}],
      "drugs": [{"name": "Atenolol", "dose": "50 mg", "route": "PO"}]
    }
  ],
  "reports": [                             // lab / radiology / pathology
    {
      "report_id": "R-77",
      "date": "2026-03-02",
      "type": "lab",
      "title": "Serology panel",
      "text": "HBsAg  NEGATİF, 0.24 ...",  // raw text → parsed by lab_parser
      "pdf_url": "https://…/optional.pdf"
    }
  ]
}
```

| Key | Used by | Notes |
|-----|---------|-------|
| `patient` | UI banner, clinical agent | name is masked before LLM |
| `episodes[]` | Episodes RAG, Neo4j graph | `examination_text` is chunked & retrieved |
| `reports[]` | Reports RAG, `lab_parser`, trends | `text` is parsed for lab values |
| `izlem[]` _(optional)_ | Monitoring RAG | vitals / flowsheet / drug-administration rows |

> [!TIP]
> Extra keys are harmless — they're ignored unless an agent looks for them.
> Start minimal (`patient` + `episodes`), then enrich.

## 🛠️ Step-by-step: build your adapter

1. **Create** `src/backend/tools/my_ehr.py`.
2. **Implement** `auto_fetch_patient(protocol_id)` returning the shape above.
3. **Wire it into the selector.** Add a branch in `tools/ehr.py` and select it via
   the `EHR_ADAPTER` env var (the orchestrator imports `auto_fetch_patient` from
   `tools/ehr.py`, so no orchestrator edit is needed):
   ```python
   # tools/ehr.py
   if settings.ehr_adapter == "my_ehr":
       from src.backend.tools.my_ehr import auto_fetch_patient
   ```
4. **Add config** to `core/config.py` + `.env.example` (your `EHR_ADAPTER` value,
   base URL, token env var).
5. **Test with synthetic data** — never real PHI.

## 🔥 Example A — FHIR R4 adapter

A compact adapter that pulls a Patient + their Encounters + DiagnosticReports
from any FHIR R4 server (Epic, Cerner, HAPI, Medplum, …):

```python
# src/backend/tools/my_ehr.py
from __future__ import annotations
import os, httpx
from typing import Any

FHIR_BASE  = os.environ.get("FHIR_BASE_URL", "https://hapi.fhir.org/baseR4")
FHIR_TOKEN = os.environ.get("FHIR_TOKEN", "")

def _auth_headers() -> dict[str, str]:
    h = {"Accept": "application/fhir+json"}
    if FHIR_TOKEN:
        h["Authorization"] = f"Bearer {FHIR_TOKEN}"
    return h

async def auto_fetch_patient(protocol_id: str) -> dict[str, Any]:
    pid = protocol_id.strip()
    async with httpx.AsyncClient(timeout=30, headers=_auth_headers()) as c:
        patient = (await c.get(f"{FHIR_BASE}/Patient/{pid}")).json()
        enc = (await c.get(f"{FHIR_BASE}/Encounter", params={"patient": pid})).json()
        rpt = (await c.get(f"{FHIR_BASE}/DiagnosticReport", params={"patient": pid})).json()

    name = patient.get("name", [{}])[0]
    return {
        "patient": {
            "full_name": f"{' '.join(name.get('given', []))} {name.get('family', '')}".strip(),
            "sex": patient.get("gender"),
            "mrn": pid,
        },
        "episodes": [
            {
                "episode_id": e["resource"].get("id"),
                "date": e["resource"].get("period", {}).get("start", ""),
                "service": (e["resource"].get("serviceType", {})
                            .get("text", "")),
                "examination_text": e["resource"].get("reasonCode", [{}])[0]
                                     .get("text", ""),
            }
            for e in enc.get("entry", [])
        ],
        "reports": [
            {
                "report_id": r["resource"].get("id"),
                "date": r["resource"].get("effectiveDateTime", ""),
                "type": "lab",
                "title": r["resource"].get("code", {}).get("text", "Report"),
                "text": r["resource"].get("conclusion", ""),
            }
            for r in rpt.get("entry", [])
        ],
    }
```

```bash
# .env
FHIR_BASE_URL=https://your-fhir-server/baseR4
FHIR_TOKEN=eyJhbGc...
```

That's it — PHI masking, RAG, the graph, and all agents now work against FHIR.

## 📁 Example B — Local file / CSV export

No live API? This is the **shipped default** (`EHR_ADAPTER=file`). The bundled
`tools/file_adapter.py` reads a per-patient JSON file, searching `$PATIENT_DATA_DIR`,
`patient_data/`, the repo root, and `examples/` (so the checked-in
`examples/patient_DEMO.json` resolves with no setup). The core idea:

```python
import json
from pathlib import Path
from typing import Any

EXPORT_DIR = Path("patient_data")   # gitignored

async def auto_fetch_patient(protocol_id: str) -> dict[str, Any]:
    path = EXPORT_DIR / f"patient_{protocol_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"No export for {protocol_id} in {EXPORT_DIR}")
    return json.loads(path.read_text(encoding="utf-8"))
```

**Try it on a fresh clone:** query the id `DEMO` (reads `examples/patient_DEMO.json`),
or drop your own synthetic `patient_<id>.json` into `patient_data/`:

```bash
mkdir -p patient_data
cp examples/patient_DEMO.json patient_data/patient_12345.json   # then query "12345 ..."
```

The `cerebral` adapter also uses this file layout as its **cache** — it writes
`patient_<id>.json` after the first scrape so repeat queries skip the EHR.

## 🔐 Authentication patterns

| Pattern | When | How |
|---------|------|-----|
| 🔑 **Bearer / OAuth token** | FHIR, modern REST APIs | `Authorization: Bearer <token>` from an env var |
| 🍪 **Session cookie** | Legacy web HBYS (the reference adapter) | Export browser cookies → convert → send as `Cookie:` header. Keep cookies in `cookies/` (**gitignored**). |
| 🪪 **mTLS / client cert** | Hospital intranet | Pass `cert=(crt, key)` to `httpx.AsyncClient` |
| 🧱 **VPN-gated host** | On-prem only | The host is unreachable from the public internet; document that the backend must run inside the hospital network |

> [!WARNING]
> **Never commit credentials.** Tokens, cookies, client certs, and patient
> exports must all be `.gitignore`d. See the repo's `.gitignore` — it already
> excludes `cookies/*.json`, `patient_*.json`, and `scripts/cerebral_*.py`.

## 🧪 How lab reports are parsed

Raw report `text` is turned into structured lab values by
`src/backend/tools/lab_parser.py`, which auto-detects **three layouts**:

| Format | Looks like | Handled by |
|--------|-----------|-----------|
| ↔️ **Horizontal** | `Glucose   95   70–110   mg/dL` (name, value, range, unit on one line) | `_parse_horizontal` |
| ↕️ **Vertical** | name / value / range on separate lines | `_parse_vertical` |
| 🧫 **Serology** | combined textual+numeric, e.g. `HBsAg  NEGATİF, 0.24` with ref `POZİTİF, >10.0`, plus `SINIR DEĞER` (borderline) ranges | `_parse_serology` |

The parser:
- Distinguishes **results** (`NEGATİF, 0.24`) from **reference values**
  (`POZİTİF, >10.0`) by the `<`/`>`/`=>` prefix on references.
- Skips accreditation IDs (`925125`), method tags (`CMİA`/`CLİA`), and `ODS` tags.
- Flags out-of-range values as `abnormal`, feeding the **trend monitor** chart and
  critical-value highlighting in the UI.

To support a **new lab format/language**, add a parser branch and wire it into
`parse_lab_report(...)` (it tries horizontal → vertical → serology in order).
Add a synthetic sample to the tests.

## 🗃️ Caching & performance

- **Cache first.** `auto_fetch_patient` should check a local cache before hitting
  the EHR (the reference adapter caches to `patient_<id>.json`).
- **Truncate huge records.** The reference adapter caps episodes at 80 (newest
  first) to avoid downstream LLM timeouts — do the same for very large histories.
- **Set realistic timeouts.** Scraping many pages can take minutes; the reference
  adapter uses a 600 s fetch timeout with a partial-data retry.

## ✅ Compliance checklist

- [ ] Adapter returns the documented patient dict shape
- [ ] Identifier normalization (spaces/dashes stripped)
- [ ] Local cache implemented (skip the EHR on repeat queries)
- [ ] Credentials read from env / gitignored files — **nothing committed**
- [ ] Patient exports written to a **gitignored** directory
- [ ] PHI masking left intact (don't bypass `phi_checker`)
- [ ] Tested with **synthetic** data only
- [ ] New config documented in `.env.example`

---

<div align="center">

Questions about wiring up a specific EHR? Open a
[discussion](https://github.com/ArioMoniri/cerebralink/discussions) — we'd love to
grow a library of community adapters. 🌍

</div>
