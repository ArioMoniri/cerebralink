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

<table>
<tr>
<td valign="top">

**Get started**
- [💡 What It Solves](#-what-it-solves)
- [🎬 Screenshots](#-screenshots)
- [🚀 How to Set Up](#-how-to-set-up)
- [⚙️ Configuration](#️-configuration)

</td>
<td valign="top">

**Under the hood**
- [🧠 Agentic Architecture](#-agentic-architecture)
- [🌊 The Streaming Pipeline](#-the-streaming-pipeline)
- [📊 Anatomy of a Query](#-anatomy-of-a-query)
- [🎨 Animated Assets](#-animated-assets)

</td>
<td valign="top">

**Integrate & extend**
- [🗂️ Data Sources & Retrieval](#️-data-sources--retrieval)
- [🔌 EHR Integration](#-ehr-integration)
- [🧩 Project Structure](#-project-structure)
- [🛠️ Tech Stack](#️-tech-stack)

</td>
<td valign="top">

**Community**
- [🤝 Contributing](#-contributing)
- [🗺️ Roadmap](#️-roadmap)
- [📜 License](#-license)

</td>
</tr>
</table>

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

<details open>
<summary><b>🔬 The full agent roster</b> — click to collapse</summary>

<br/>

| Agent | Model Tier | Does |
|-------|:---------:|------|
| 🧭 Router | 🟦 Haiku | Classifies the query & picks which agents to run |
| 🛡️ PHI Masker | 🟦 Haiku | Removes identifiers before any reasoning LLM sees the data |
| 🔬 Research | 🟪 Sonnet | Latest guidelines & literature (Exa + MCP) |
| 💊 Drug | 🟪 Sonnet | Interactions, contraindications, dosing |
| 🩺 Clinical | 🟣 Opus | Deep reasoning grounded in patient context |
| 📝 Prescription | 🟪 Sonnet | ATC mapping + country brand options |
| 🏥 Episodes | 🟪 Sonnet | Reasons over admission/episode RAG |
| 📈 İzlem | 🟪 Sonnet | Reasons over monitoring/vitals RAG |
| ⚡ Fast Composer | 🟪 Sonnet | The instant partial answer (`max_tokens=3072`) |
| 📚 Full Composer | 🟪 Sonnet | The deep, cited answer (`max_tokens=8192`) |
| ⚖️ Trust Scorer | 🟦 Haiku | Six-dimension confidence scoring |
| 🌳 Decision Tree | 🟪 Sonnet | Builds the visual reasoning tree |

</details>

> [!NOTE]
> Agents within a phase run **concurrently** via `asyncio` with a 90 s per-agent
> timeout. A slow agent never blocks the others — results are collected as they
> complete (`asyncio.as_completed`).

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

## 📊 Anatomy of a Query

<div align="center">
<img src="docs/assets/metrics.svg" alt="Per-agent timings and token usage" width="100%"/>
</div>

A look inside one representative request — how long each agent takes and where the
tokens go.

> [!TIP]
> The bars show **per-agent** processing time, but phases ② and ③ run
> **concurrently** — so the wall-clock time is far less than the sum. The clinician
> sees a `fast_answer` in about **2 seconds** while the deep analysis keeps composing.

<details>
<summary><b>📈 What the numbers mean</b></summary>

<br/>

| Metric | Typical | Notes |
|--------|:------:|-------|
| ⏱️ Time to `fast_answer` | **~2 s** | First useful answer streamed to the UI |
| ⏱️ Time to full `result` | **1–3 min** | Deep, cited analysis + trust scores |
| 🎟️ Tokens / query | **≈26k** | ~18.5k input · ~7.7k output (varies with patient context) |
| 🧠 Agents / query | **3–9** | The Router decides which agents are needed |
| 💸 Cost lever | model tiers | Haiku for cheap/structured work, Sonnet/Opus for reasoning |

Numbers are illustrative (captured from a real drug-dosing query) and depend on the
question, patient-context size, and which agents the Router activates.

</details>

## 🎨 Animated Assets

CerebraLink ships **two kinds** of motion graphics:

> **① Animated SVGs** render **directly on GitHub** (CSS keyframes + SMIL motion,
> zero dependencies) · **② Lottie JSON** drives richer animations inside the
> running app.

#### 🎞️ Animated SVGs — `docs/assets/*.svg`

| File | Shows |
|------|-------|
| 🦸 `hero.svg` | Animated wordmark with a sweeping gradient + a flowing neural network |
| 🧠 `architecture.svg` | The agent council with live signal dots traveling the pipeline |
| 🌊 `pipeline.svg` | The SSE event timeline with packets flowing left → right |
| 📊 `metrics.svg` | Per-agent latency bars + a token donut that draw in on load |

#### 🪄 Lottie JSON — `docs/assets/lottie/*.json`

| File | Use it as |
|------|-----------|
| 🌀 `neural-pulse.json` | A "thinking…" loader while agents work |
| 🕸️ `agent-council.json` | A hero/explainer of the multi-agent council |

<details>
<summary><b>▶️ Embed Lottie — plain HTML (CDN, no build)</b></summary>

```html
<script src="https://unpkg.com/@lottiefiles/lottie-player@latest/dist/lottie-player.js"></script>

<lottie-player src="docs/assets/lottie/neural-pulse.json"
  background="transparent" speed="1" loop autoplay
  style="width: 240px; height: 240px;">
</lottie-player>
```
</details>

<details>
<summary><b>⚛️ Embed Lottie — Next.js / React</b></summary>

```bash
cd src/frontend && npm install lottie-react
```
```tsx
// src/frontend/src/components/ThinkingLoader.tsx
"use client";
import Lottie from "lottie-react";
import neuralPulse from "../../../docs/assets/lottie/neural-pulse.json";

export function ThinkingLoader() {
  return <Lottie animationData={neuralPulse} loop autoplay style={{ width: 120, height: 120 }} />;
}
// …then render it while the SSE pipeline runs:  {isLoading && <ThinkingLoader />}
```
</details>

<details>
<summary><b>🎛️ Customize colors &amp; timing</b></summary>

<br/>

Everything is hand-authored and editable in a text editor:

- **Lottie** — edit each layer's fill/stroke `c` (RGBA 0–1 arrays): teal
  `[0.369,0.918,0.831,1]`, indigo `[0.506,0.549,0.973,1]`, violet
  `[0.753,0.518,0.988,1]`. Retime via keyframe `t` values (30 fps, 90-frame loop),
  or open in the [LottieFiles Editor](https://lottiefiles.com/).
- **SVG** — edit the `<linearGradient>` stops and the `<style>` `@keyframes` /
  `<animate>` `dur` values in any vector tool or text editor.

</details>

## 🚀 How to Set Up

Up and running in **four steps** (~3 min + image build). 🐳

#### ✅ Prerequisites

| Need | Why | Get it |
|------|-----|--------|
| 🐳 **Docker + Compose** | Runs the whole stack | [docker.com](https://www.docker.com/products/docker-desktop/) |
| 🔑 **Anthropic API key** | All agent reasoning (**required**) | [console.anthropic.com](https://console.anthropic.com/) |
| 🔎 **Exa API key** | Latest-guideline search (recommended) | [exa.ai](https://exa.ai/) |

#### 🧭 Steps

```bash
# 1️⃣  Clone
git clone https://github.com/ArioMoniri/cerebralink.git && cd cerebralink

# 2️⃣  Configure — copy the template, then add your keys
cp .env.example .env
#    edit .env → ANTHROPIC_API_KEY=sk-ant-...   (EXA_API_KEY=... recommended)

# 3️⃣  Launch the full stack 🚀  (frontend + backend + Redis + Neo4j + MCP sidecars)
docker compose up -d --build

# 4️⃣  Open the app
open http://localhost:3100        # or just visit it in your browser
```

> [!IMPORTANT]
> On first boot, the **MCP sidecars install npm packages** — they can take a
> couple of minutes to report healthy. That's expected. Watch with
> `docker compose ps`.

<details>
<summary><b>🔍 Verify it's working</b></summary>

<br/>

```bash
docker compose ps                                   # all services → "healthy"
curl -s localhost:8100/health                       # → {"status":"ok","service":"cerebralink"}
curl -s localhost:3100/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"what is the adult dose of paracetamol?"}' | head -c 200
```
Then open <http://localhost:3100> and ask a clinical question — you should see the
**Fast / Full / Highlights** tabs stream in.

</details>

<details>
<summary><b>🖥️ Run natively (without Docker)</b></summary>

<br/>

```bash
# Backend
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r src/backend/requirements.txt
export $(grep -v '^#' .env | xargs)
PYTHONPATH=. uvicorn src.backend.api.app:app --reload --port 8000

# Frontend (new terminal)
cd src/frontend && npm install
BACKEND_URL=http://localhost:8000 npm run dev        # → http://localhost:3000
```
You'll still want Redis + Neo4j: `docker compose up -d redis neo4j`.
Full guide: [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md#-local-development-without-docker).

</details>

<details>
<summary><b>🩹 Troubleshooting</b></summary>

<br/>

| Symptom | Fix |
|---------|-----|
| ⏳ A sidecar stays "unhealthy" for >3 min | It's still `npm install`-ing — check `docker compose logs <service>` |
| 🔌 `Backend connection failed` in the UI | `docker compose restart frontend` (re-resolves the backend DNS after a rebuild) |
| 🧱 Neo4j won't start | `docker compose restart neo4j` then `docker compose up -d` |
| 🔑 Empty / 401 answers | Check `ANTHROPIC_API_KEY` in `.env`, then `docker compose up -d backend` |
| 🐌 Slow first response | Cold start + guideline search — subsequent queries are faster |

</details>

## ⚙️ Configuration

All settings live in `.env` (template: `.env.example`) and resolve through
`src/backend/core/config.py`. **The only thing you must set is your API key:**

```bash
ANTHROPIC_API_KEY=sk-ant-...         # required — all agent reasoning
EXA_API_KEY=...                      # recommended — latest-guideline search
```

> [!CAUTION]
> Never commit your `.env`, cookies, or any patient data. They're already in
> `.gitignore` — keep them there.

<details>
<summary><b>⚙️ Full environment reference (model tiers, infra, MCP)</b></summary>

```bash
# ── Model tiers — override any agent's model ──
MODEL_ROUTER=claude-haiku-4-5-20251001
MODEL_CLINICAL=claude-opus-4-6
MODEL_RESEARCH=claude-sonnet-4-6
MODEL_DRUG=claude-sonnet-4-6
MODEL_COMPOSER=claude-sonnet-4-6
MODEL_TRUST=claude-haiku-4-5-20251001

# ── Infra (defaults work out-of-the-box with docker-compose) ──
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

| Tier | Default model | Agents | Why |
|:----:|---------------|--------|-----|
| 🟦 1 | `claude-haiku-4-5` | Router, PHI Masker, Trust | cheap · fast · structured |
| 🟪 2 | `claude-sonnet-4-6` | Research, Drug, Composers, Rx | balanced reasoning |
| 🟣 3 | `claude-opus-4-6` | Clinical | deepest clinical reasoning |

</details>

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

<details>
<summary><b>📂 Expand the repository tree</b></summary>

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

</details>

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
