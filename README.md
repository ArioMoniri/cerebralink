<div align="center">

<img src="docs/assets/hero.svg" alt="CerebraLink — Multi-Agent Clinical Decision Support" width="100%"/>

<br/>

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-5eead4.svg?style=flat-square)](./LICENSE)
[![CI](https://img.shields.io/badge/CI-frontend%20%7C%20backend%20%7C%20docker-818cf8?style=flat-square)](./.github/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=flat-square&logo=next.js&logoColor=white)](https://nextjs.org/)
[![Claude](https://img.shields.io/badge/Claude-Haiku_·_Sonnet_·_Opus-c084fc?style=flat-square)](https://www.anthropic.com/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](./CONTRIBUTING.md)

**A streaming, multi-agent clinical decision-support assistant.**
Ask a clinical question → seven specialized AI agents deliberate in parallel →
get a fast answer in ~2 seconds, then a deep, cited, trust-scored analysis. 🧠⚡🔬

[✨ Features](#-what-it-solves) ·
[🧠 Architecture](#-agentic-architecture) ·
[🚀 Quick Start](#-quick-start) ·
[🎨 Animations](#-animated-assets--lottie) ·
[🔌 EHR Integration](#-ehr-integration) ·
[🤝 Contributing](#-contributing)

</div>

---

> [!WARNING]
> 🩺 **Medical disclaimer.** CerebraLink is a clinical **decision-support** and
> research tool — **not** a medical device and **not** a substitute for
> professional medical judgment. Every output must be independently verified by a
> licensed clinician before any clinical use. See the [NOTICE](./NOTICE).

## 📑 Table of Contents

- [💡 What It Solves](#-what-it-solves)
- [🎬 Screenshots](#-screenshots)
- [🧠 Agentic Architecture](#-agentic-architecture)
- [🌊 The Streaming Pipeline](#-the-streaming-pipeline)
- [🎨 Animated Assets — Lottie](#-animated-assets--lottie)
- [🚀 Quick Start](#-quick-start)
- [⚙️ Configuration](#️-configuration)
- [🗂️ Data Sources & Retrieval](#️-data-sources--retrieval)
- [🔌 EHR Integration](#-ehr-integration)
- [🧩 Project Structure](#-project-structure)
- [🛠️ Tech Stack](#️-tech-stack)
- [🤝 Contributing](#-contributing)
- [🗺️ Roadmap](#️-roadmap)
- [📜 License](#-license)

## 💡 What It Solves

Clinicians are time-poor and drowning in fragmented information. A single dosing
question can mean cross-checking guidelines, drug interactions, the patient's
history, and local formularies — across half a dozen tabs. CerebraLink collapses
that into **one question and one streamed answer**.

| ❌ The Problem | ✅ CerebraLink's Answer |
|---------------|------------------------|
| Guidelines, drug data, and patient history live in separate systems | A **multi-agent council** queries them all in parallel |
| LLM medical answers are slow and unsourced | **Fast answer in ~2 s**, then a deep answer with **verifiable citations** |
| You can't tell if an AI answer is trustworthy | Every answer carries **trust scores** (evidence, alignment, safety, recency) |
| Generic chatbots ignore the actual patient | **EHR-aware**: pulls labs, episodes, monitoring via a pluggable adapter |
| Patient data leaking to LLMs is a non-starter | **PHI is masked** before anything reaches a reasoning model |
| Prescriptions need local brand names | **ATC mapping + country-specific brand options** with a searchable picker |
| Hallucinated reference links | Citation URLs are **verified to resolve** before display |

### 🌟 Highlights

- 🧠 **7+ specialized agents** — router, research, drug, clinical, prescription, composers, trust scorer
- ⚡ **Dual-speed answers** — a `fast_answer` streams in ~2 s; the full analysis follows
- 🔬 **Cited evidence** — guidelines & literature from Exa, PubMed, openFDA, and more
- ⚖️ **Trust scoring** — transparent confidence across six dimensions
- 🩺 **EHR-aware** — pluggable adapter (FHIR, legacy HBYS, file export…) + RAG over reports/episodes/monitoring
- 🛡️ **Privacy-first** — PHI masking before LLM, verified citations, decision-support framing
- 🧫 **Smart lab parsing** — horizontal, vertical & serology report layouts (multi-language)
- 🕸️ **Knowledge graph** — Neo4j links patients ↔ episodes ↔ reports ↔ drugs, visualized in-app
- 🎨 **Liquid-glass UI** — Next.js 14, animated, with Fast/Full/Highlights tabs

## 🎬 Screenshots

> 🎨 The previews below are **UI mockups** that render everywhere. Replace them
> with real captures of your running instance anytime (see the tip below).

| Chat with Fast / Full / Highlights tabs | Trust gauges & verified references |
|:---:|:---:|
| <img src="docs/assets/screenshots/chat.svg" alt="Chat view" width="420"/> | <img src="docs/assets/screenshots/trust.svg" alt="Trust gauges" width="420"/> |
| **Prescription card with searchable brand picker** | **Neo4j knowledge graph & lab trends** |
| <img src="docs/assets/screenshots/prescription.svg" alt="Prescription card" width="420"/> | <img src="docs/assets/screenshots/graph.svg" alt="Knowledge graph" width="420"/> |

<details>
<summary>📷 How to add real screenshots</summary>

```bash
docker compose up -d            # boot the stack
open http://localhost:3100      # ask, e.g. "paracetamol dosing in hepatic impairment"
# Capture each panel and save as PNG into docs/assets/screenshots/,
# then point the <img> tags above at your .png files.
```
The diagrams elsewhere in this README come from `docs/assets/*.svg` and **animate
directly on GitHub** — no setup required. ✨
</details>

## 🧠 Agentic Architecture

<div align="center">
<img src="docs/assets/architecture.svg" alt="CerebraLink agentic architecture" width="100%"/>
</div>

A clinical question flows through **five phases**, with agents running concurrently
inside each phase:

```
① ROUTE      → 🧭 Router (Haiku): classify intent, language, urgency
② FETCH+MASK → 🗂️ EHR adapter pulls record → 🛡️ PHI Masker de-identifies
③ COUNCIL    → 🔬 Research ‖ 💊 Drug ‖ 🩺 Clinical ‖ 📝 Prescription  (parallel)
④ COMPOSE    → ⚡ Fast Composer (streams ~2 s)  →  📚 Full Composer (deep, cited)
⑤ SCORE      → ⚖️ Trust Scorer: evidence · alignment · safety · recency
```

| Agent | Model Tier | Does |
|-------|:---------:|------|
| 🧭 Router | 🟦 Haiku | Classifies the query & picks which agents to run |
| 🛡️ PHI Masker | 🟦 Haiku | Removes identifiers before any reasoning LLM sees the data |
| 🔬 Research | 🟪 Sonnet | Latest guidelines & literature (Exa + MCP) |
| 💊 Drug | 🟪 Sonnet | Interactions, contraindications, dosing |
| 🩺 Clinical | 🟣 Opus | Deep reasoning grounded in patient context |
| 📝 Prescription | 🟪 Sonnet | ATC mapping + country brand options |
| ⚡ Fast Composer | 🟪 Sonnet | The instant partial answer (`max_tokens=3072`) |
| 📚 Full Composer | 🟪 Sonnet | The deep, cited answer (`max_tokens=8192`) |
| ⚖️ Trust Scorer | 🟦 Haiku | Six-dimension confidence scoring |

📖 **Full deep-dive:** [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md)

## 🌊 The Streaming Pipeline

<div align="center">
<img src="docs/assets/pipeline.svg" alt="SSE streaming timeline" width="100%"/>
</div>

The browser opens **one** `POST /api/chat/stream` and receives typed
**Server-Sent Events** as each agent finishes:

| Event | Arrives | Carries |
|-------|---------|---------|
| `status` | continuously | which agent is running/done, timing, tokens |
| `fast_answer` | ~1–2 s | the partial answer + early citations |
| `result` | on completion | full answer, trust scores, decision tree, timings |
| `done` | end | stream close |

A Next.js route handler proxies the stream and injects `:keepalive` comments every
15 s so reverse proxies / tunnels never drop the idle connection during long
reasoning.

## 🎨 Animated Assets — Lottie

CerebraLink ships **two kinds** of motion graphics:

1. **Animated SVGs** (`docs/assets/*.svg`) — the diagrams above. They animate
   **directly in this README** (GitHub runs the embedded CSS keyframes) with zero
   dependencies. Use these for docs & GitHub.
2. **Lottie JSON** (`docs/assets/lottie/*.json`) — vector animations for the
   **running app** (a thinking-loader and an animated agent-council). Lottie can't
   run inside a GitHub README, so use it in the web app / docs site.

| File | Use it as |
|------|-----------|
| 🌀 `docs/assets/lottie/neural-pulse.json` | A "thinking…" loader while agents work |
| 🕸️ `docs/assets/lottie/agent-council.json` | A hero/explainer of the multi-agent council |

### ▶️ How to use Lottie — in any HTML page (CDN, no build)

```html
<script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>

<lottie-player
  src="docs/assets/lottie/neural-pulse.json"
  background="transparent"
  speed="1"
  style="width: 240px; height: 240px;"
  loop autoplay>
</lottie-player>
```

### ⚛️ How to use Lottie — in the Next.js frontend

```bash
cd src/frontend
npm install lottie-react
```

```tsx
// src/frontend/src/components/ThinkingLoader.tsx
"use client";
import Lottie from "lottie-react";
import neuralPulse from "../../../docs/assets/lottie/neural-pulse.json";

export function ThinkingLoader() {
  return (
    <Lottie
      animationData={neuralPulse}
      loop
      autoplay
      style={{ width: 120, height: 120 }}
    />
  );
}
```

```tsx
// Use it anywhere — e.g. while the SSE pipeline is running:
{isLoading && <ThinkingLoader />}
```

> [!TIP]
> 🎛️ **Customize the animation:** the Lottie files are hand-authored Bodymovin
> JSON. Edit colors via each layer's fill/stroke `c` (RGBA 0–1 arrays:
> teal `[0.369,0.918,0.831,1]`, indigo `[0.506,0.549,0.973,1]`, violet
> `[0.753,0.518,0.988,1]`), retime via keyframe `t` values (30 fps, 90-frame loop),
> or open them in [LottieFiles Editor](https://lottiefiles.com/) / After Effects +
> Bodymovin. The animated SVGs are editable in any text editor or vector tool.

## 🚀 Quick Start

> **Prerequisites:** Docker + Docker Compose, and an
> [Anthropic API key](https://console.anthropic.com/). An
> [Exa key](https://exa.ai/) is recommended for guideline search.

```bash
# 1️⃣  Clone
git clone https://github.com/ArioMoniri/cerebralink.git
cd cerebralink

# 2️⃣  Configure
cp .env.example .env
#    → set ANTHROPIC_API_KEY (required), EXA_API_KEY (recommended)

# 3️⃣  Launch the full stack 🚀
docker compose up -d --build

# 4️⃣  Open the app
open http://localhost:3100
```

That's it — frontend (`:3100`), backend (`:8100`), Redis, Neo4j, and the MCP
sidecars all boot together. MCP sidecars install packages on first run, so give
them a couple of minutes to become healthy.

```bash
docker compose ps          # watch health
docker compose logs -f backend
```

🖥️ Prefer running natively (no Docker)? See
[`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md#-local-development-without-docker).

## ⚙️ Configuration

All settings live in `.env` (template: `.env.example`) and resolve through
`src/backend/core/config.py`.

```bash
# ── Required ──
ANTHROPIC_API_KEY=sk-ant-...

# ── Recommended ──
EXA_API_KEY=...                      # latest-guideline search

# ── Model tiers (override any agent's model) ──
MODEL_ROUTER=claude-haiku-4-5-20251001
MODEL_CLINICAL=claude-opus-4-6
MODEL_RESEARCH=claude-sonnet-4-6
MODEL_DRUG=claude-sonnet-4-6
MODEL_COMPOSER=claude-sonnet-4-6
MODEL_TRUST=claude-haiku-4-5-20251001

# ── Infra (defaults work with docker-compose) ──
REDIS_URL=redis://redis:6379/0
NEO4J_URI=bolt://neo4j:7687
NEO4J_AUTH=neo4j/cerebralink2024

# ── MCP sidecars ──
HEALTHCARE_MCP_URL=http://healthcare-mcp:3002
MEDICAL_KNOWLEDGE_MCP_URL=http://medical-knowledge-mcp:3004
OMOPHUB_MCP_URL=http://omophub-mcp:3005
OMOPHUB_API_KEY=...
FDC_API_KEY=...                      # USDA FoodData Central (optional)
```

## 🗂️ Data Sources & Retrieval

CerebraLink fuses **live APIs**, **MCP sidecars**, **RAG**, and a **graph**:

| Source | Via | Provides |
|--------|-----|----------|
| 🤖 Anthropic Claude | `agents/base.py` | All reasoning |
| 🔎 Exa.ai | `tools/exa.py` | Country-aware latest guidelines |
| 🏥 Healthcare MCP | sidecar `:3102` | openFDA, PubMed, ClinicalTrials.gov, ICD-10, medRxiv |
| 📚 Medical-Knowledge MCP | sidecar `:3104` | FDA, WHO, RxNorm, Google Scholar, pediatric |
| 🗃️ OMOPHub MCP | sidecar `:3105` | OMOP CDM terminology (SNOMED, ICD-10, RxNorm, LOINC) |
| 🍎 Food Data MCP | sidecar `:3103` | USDA nutrition (optional) |
| 📄 Reports RAG | `tools/reports_rag.py` | Lab/radiology/pathology retrieval |
| 🏥 Episodes RAG | `tools/episodes_rag.py` | Admission/discharge retrieval |
| 📈 İzlem RAG | `tools/izlem_rag.py` | Monitoring/vitals retrieval |
| 🕸️ Neo4j Graph | `tools/graph.py` | Patient ↔ report ↔ episode ↔ drug relations |

Documents are chunked with paragraph/sentence-aware splitting and entity extraction
(labs, dates, ICD codes). Lab text is parsed by `tools/lab_parser.py` into
structured, trend-able values across three report layouts.

## 🔌 EHR Integration

CerebraLink talks to your EHR through a **single pluggable adapter** — one async
function that returns a normalized patient dict. PHI masking, RAG, the graph, and
all agents are EHR-agnostic.

> [!IMPORTANT]
> 🔒 The institution-specific scraping scripts used in development (Acıbadem
> CerebralPlus / `scripts/cerebral_*.py`) are **deliberately kept local and not
> distributed** (they're `.gitignore`d, along with cookies, the drug DB, and any
> cached patient data). Bring your own EHR by writing an adapter.

```python
# The entire contract — implement this and you're done:
async def auto_fetch_patient(protocol_id: str) -> dict[str, Any]:
    """Resolve an identifier to a normalized patient dict
       ({patient, episodes[], reports[], …}). Cache locally; then hit the EHR."""
```

✅ Ready-made examples in the guide — **FHIR R4** (Epic/Cerner/HAPI/Medplum), a
**local file/CSV export** adapter, auth patterns (OAuth, cookies, mTLS, VPN), and
how lab parsing works:

📖 **[`docs/EHR_ADAPTER.md`](./docs/EHR_ADAPTER.md)**

## 🧩 Project Structure

```
cerebralink/
├── 📂 src/
│   ├── 📂 backend/            # FastAPI + the agent council (Python 3.12)
│   │   ├── api/               # app, routes, schemas
│   │   ├── agents/            # router, research, drug, clinical, composer, trust…
│   │   ├── core/              # config, memory (Redis), orchestrator (SSE pipeline)
│   │   └── tools/             # exa, graph, lab_parser, *_mcp, *_rag, EHR adapter
│   └── 📂 frontend/           # Next.js 14 UI
│       └── src/
│           ├── app/           # chat shell + SSE proxy route handler
│           └── components/    # message bubble, trust gauges, graphs, trends…
├── 📂 docs/
│   ├── ARCHITECTURE.md        # deep architecture dive
│   ├── EHR_ADAPTER.md         # how to connect your EHR
│   └── assets/                # animated SVGs + Lottie JSON
├── 📂 scripts/                # MCP bridge, ingest helpers (EHR scrapers kept local 🔒)
├── 🐳 docker-compose.yml      # the full stack
├── 🐳 Dockerfile.backend / .frontend / .medical-mcp
├── 📜 NOTICE / LICENSE        # Apache 2.0 © Ariorad Moniri
├── 🤝 CONTRIBUTING.md / CODE_OF_CONDUCT.md
└── 📄 .env.example
```

## 🛠️ Tech Stack

**Backend** 🐍 FastAPI · uvicorn · Anthropic SDK · Pydantic · Redis · Neo4j ·
httpx · PyMuPDF · BeautifulSoup · SSE-Starlette

**Frontend** ⚛️ Next.js 14 · React 18 · TypeScript · Tailwind · Framer Motion ·
anime.js · @xyflow/react · Recharts · react-markdown · KaTeX · Lucide

**Infra** 🐳 Docker Compose · Model Context Protocol (MCP) sidecars · GitHub Actions CI

## 🤝 Contributing

Contributions of every size are welcome — from typo fixes to whole new agents and
EHR adapters! 💙

1. 📖 Read [`CONTRIBUTING.md`](./CONTRIBUTING.md) and the
   [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md)
2. 🍴 Fork & branch (`feat/…`, `fix/…`, `docs/…`)
3. ✅ Make sure CI passes (`tsc --noEmit`, backend imports, `docker compose config`)
4. 🩺 Follow the **clinical safety rules** — **never** commit real patient data
5. 🔁 Open a PR with the checklist filled in

Great first contributions: a new **MCP data source**, an **EHR adapter** (Epic,
OpenEMR, FHIR), a **lab-report parser** for a new format/language, or **UI/a11y**
improvements.

## 🗺️ Roadmap

- [ ] 🌍 Community library of EHR adapters (FHIR, OpenEMR, Epic)
- [ ] 🧪 Expanded synthetic test fixtures for lab parsers
- [ ] 🗣️ More UI languages (i18n)
- [ ] 📊 Configurable trust-scoring rubrics
- [ ] 🔁 Optional self-hosted / local model backends
- [ ] 🧩 Plugin API for custom agents

## 📜 License

Licensed under the **[Apache License 2.0](./LICENSE)** — © 2026 **Ariorad Moniri**.

You're free to use, modify, and distribute this software (including commercially)
under the terms of the license. See [`NOTICE`](./NOTICE) for attribution,
third-party data-source terms, and the medical disclaimer.

---

<div align="center">

**Built with 💙 for clinicians and engineers** — by [Ariorad Moniri](https://github.com/ArioMoniri) & contributors.

⭐ _If CerebraLink is useful to you, consider starring the repo!_ ⭐

</div>
