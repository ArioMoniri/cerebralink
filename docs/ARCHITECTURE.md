<div align="center">

# 🏛️ CerebraLink Architecture

_How a single clinical question becomes a streamed, cited, trust-scored answer._

<img src="./assets/architecture.svg" alt="CerebraLink agentic architecture" width="100%"/>

</div>

---

## 📑 Table of Contents

- [🗺️ System Overview](#️-system-overview)
- [🧩 Services (Docker Compose)](#-services-docker-compose)
- [🧠 The Agent Council](#-the-agent-council)
- [🎚️ 3-Tier Model Routing](#️-3-tier-model-routing)
- [🌊 The SSE Streaming Pipeline](#-the-sse-streaming-pipeline)
- [🧬 Memory & Retrieval (RAG + Graph)](#-memory--retrieval-rag--graph)
- [🔌 MCP Sidecars & Data Sources](#-mcp-sidecars--data-sources)
- [🛡️ PHI Masking & Safety](#️-phi-masking--safety)
- [🧱 Backend Module Map](#-backend-module-map)
- [🎨 Frontend Component Map](#-frontend-component-map)
- [🧰 Extending the System](#-extending-the-system)
- [💻 Local Development without Docker](#-local-development-without-docker)

## 🗺️ System Overview

CerebraLink is a **multi-agent clinical decision-support** system. A query flows
through five phases — **Route → Fetch+Mask → Council → Compose → Score** — and the
answer is streamed back to the browser token-event by token-event over a single
**Server-Sent Events (SSE)** connection.

```
Browser (Next.js)
   │  POST /api/chat/stream
   ▼
Next.js Route Handler  ──(proxy + :keepalive)──►  FastAPI Backend
                                                      │
                                                      ▼
                                            Orchestrator (asyncio)
                                       ┌──────────────┼───────────────┐
                                       ▼              ▼               ▼
                                   Router        Council agents    Composers
                                  (Haiku)     (Sonnet / Opus)     (Sonnet)
                                       │              │               │
                                       ▼              ▼               ▼
                                  Redis (session)  Neo4j (graph)   MCP sidecars
                                                                   + Exa + Claude
```

## 🧩 Services (Docker Compose)

| Service | Port (host→container) | Role |
|---------|------------------------|------|
| 🖥️ `frontend` | `3100 → 3000` | Next.js 14 UI + SSE proxy route handler |
| ⚙️ `backend` | `8100 → 8000` | FastAPI + uvicorn, the orchestrator & agents |
| 🧠 `neo4j` | `7474 / 7687` | Knowledge graph (patient ↔ reports ↔ episodes ↔ drugs) |
| ⚡ `redis` | `6380 → 6379` | Session memory & short-term agent memory |
| 💊 `medical-mcp` | `3101 → 3001` | General drug / interaction API bridge |
| 🏥 `healthcare-mcp` | `3102 → 3002` | openFDA, PubMed, ClinicalTrials.gov, ICD-10, medRxiv |
| 🍎 `food-data-mcp` | `3103 → 3003` | USDA FoodData Central (optional) |
| 📚 `medical-knowledge-mcp` | `3104 → 3004` | FDA, WHO, RxNorm, Google Scholar, pediatric |
| 🗂️ `omophub-mcp` | `3105 → 3005` | OMOP CDM terminology (SNOMED, ICD-10, RxNorm, LOINC) |

> [!NOTE]
> MCP sidecars install their npm packages on first boot, so they have long
> `start_period` health-check windows (120–180 s). That's expected.

## 🧠 The Agent Council

Each agent is a small class subclassing `BaseAgent` (`src/backend/agents/base.py`),
which wraps the Anthropic SDK and tracks token usage.

| Agent | File | Model tier | Responsibility |
|-------|------|-----------|----------------|
| 🧭 **Router** | `router.py` | Haiku | Classify intent, language, urgency; decide which agents run |
| 🛡️ **PHI Masker** | `phi_masker.py` | Haiku | De-identify patient data **before** it reaches any reasoning LLM |
| 🔬 **Research** | `research.py` | Sonnet | Pull latest guidelines & literature (Exa + MCP) |
| 💊 **Drug** | `drug.py` | Sonnet | Interactions, contraindications, dosing |
| 🩺 **Clinical** | `clinical.py` | Opus | Deep clinical reasoning with patient context |
| 📝 **Prescription** | `prescription.py` | Sonnet | ATC mapping + brand options (per country) |
| 🏥 **Episodes** | `episodes.py` | Sonnet | Reason over admission/episode RAG |
| 📈 **Monitoring** | `izlem.py` | Sonnet | Reason over monitoring/vitals (flowsheet) RAG |
| ⚡ **Fast Composer** | `composer.py` | Sonnet | Compose a partial answer that streams in ~1–2 s (`max_tokens=3072`) |
| 📚 **Full Composer** | `composer.py` | Sonnet | Compose the deep, cited answer (`max_tokens=8192`) |
| ⚖️ **Trust Scorer** | `trust.py` | Haiku | Score evidence quality, guideline alignment, safety, recency |
| 🌳 **Decision Tree** | `decision_tree.py` | Sonnet | Build the visual reasoning tree |

Council agents run **concurrently** via `asyncio` with a per-agent 90 s timeout
(`orchestrator.py → _timed_agent`). Results are collected with
`asyncio.as_completed`, so a slow agent never blocks the others.

## 🎚️ 3-Tier Model Routing

Models are configurable per agent via environment variables (`core/config.py`):

| Tier | Model (default) | Used by | Why |
|------|-----------------|---------|-----|
| 🟦 Tier 1 | `claude-haiku-4-5` | Router, PHI Masker, Trust | Cheap, fast, structured |
| 🟪 Tier 2 | `claude-sonnet-4-6` | Research, Drug, Composers, Prescription | Balanced reasoning |
| 🟣 Tier 3 | `claude-opus-4-6` | Clinical | Deepest clinical reasoning |

Override any of them in `.env`:

```bash
MODEL_ROUTER=claude-haiku-4-5-20251001
MODEL_CLINICAL=claude-opus-4-6
MODEL_RESEARCH=claude-sonnet-4-6
# … see .env.example for the full list
```

## 🌊 The SSE Streaming Pipeline

<div align="center">
<img src="./assets/pipeline.svg" alt="SSE streaming timeline" width="100%"/>
</div>

The orchestrator emits typed SSE events as work completes:

| Event | Payload | When |
|-------|---------|------|
| `status` | `{agent, status, message, phase, time_ms, tokens}` | Every agent start/finish |
| `fast_answer` | `{fast_answer, citations, guidelines_used, prescription_data}` | As soon as the Fast Composer finishes (~1–2 s) |
| `result` | full `ChatResponse` (complete answer, trust scores, timings, decision tree, …) | When the full pipeline finishes |
| `error` | `{message}` | On a fatal pipeline error |
| `done` | — | Stream close |

**Why a custom route handler?** Next.js `rewrites` buffer responses, which breaks
SSE. `src/frontend/src/app/api/chat/stream/route.ts` instead pipes the backend
stream through a `ReadableStream`, and injects `:keepalive` comments every 15 s so
Cloudflare tunnels / reverse proxies don't kill the idle connection during long
reasoning. The client parser in `app/page.tsx` ignores any line that doesn't start
with `event:` or `data:`.

## 🧬 Memory & Retrieval (RAG + Graph)

CerebraLink uses a **hybrid memory** model:

```
┌─────────────────────────────────────────────────────────────┐
│  Redis            →  session state + per-agent scratch memory │
│  Neo4j            →  knowledge graph (entities & relations)   │
│  File-based RAG   →  chunked, tokenized retrieval over docs   │
└─────────────────────────────────────────────────────────────┘
```

Three RAG indices ingest patient documents (chunked with paragraph/sentence-aware
splitting + entity extraction for labs, dates, ICD codes):

| Index | Source | Module |
|-------|--------|--------|
| 📄 Reports RAG | Lab / radiology / pathology reports | `tools/reports_rag.py` |
| 🏥 Episodes RAG | Admission / discharge episodes | `tools/episodes_rag.py` |
| 📈 Monitoring RAG | Physician/nurse flowsheets, vitals, drug administration | `tools/izlem_rag.py` |

The **Neo4j graph** (`tools/graph.py`) links patients → episodes → reports →
drugs, powering the interactive graph views in the UI.

## 🔌 MCP Sidecars & Data Sources

External medical knowledge is reached through **Model Context Protocol (MCP)**
sidecars, each wrapped by `scripts/mcp-http-bridge.mjs` (stdio-MCP → HTTP). The
backend's `tools/*_mcp.py` clients call them. Plus:

- 🔎 **Exa.ai** (`tools/exa.py`) — country-aware "latest guidelines" search
- 🤖 **Anthropic Claude** (`agents/base.py`) — all reasoning
- 🔗 **Reader proxy** (`tools/reader_proxy.py`) — verifies citation URLs resolve
  before they're shown to a clinician

## 🛡️ PHI Masking & Safety

```
Patient record ──► 🛡️ PHI Masker (Haiku) ──► de-identified context ──► reasoning LLMs
```

Patient data is **masked before** it ever reaches a reasoning model. Citation URLs
are verified for resolvability. Every answer carries trust scores and preserves a
decision-support disclaimer. See [`../CONTRIBUTING.md`](../CONTRIBUTING.md#-clinical-safety-rules).

## 🧱 Backend Module Map

```
src/backend/
├── api/
│   ├── app.py            # FastAPI app + CORS
│   ├── routes.py         # /api/chat, /api/chat/stream, sessions, reports, episodes…
│   └── schemas.py        # Pydantic response models (ChatResponse, TrustScores, …)
├── agents/               # the council (see table above)
├── core/
│   ├── config.py         # single source of truth for settings & model tiers
│   ├── memory.py         # Redis-backed SessionMemory / AgentMemory
│   └── orchestrator.py   # the 5-phase pipeline & SSE emitter
└── tools/
    ├── exa.py            # guideline search
    ├── graph.py          # Neo4j knowledge graph
    ├── lab_parser.py     # horizontal / vertical / serology lab parsing
    ├── reader_proxy.py   # citation URL verification
    ├── *_mcp.py          # MCP sidecar HTTP clients
    ├── *_rag.py          # reports / episodes / izlem retrieval
    └── cerebral.py       # 🔒 EHR adapter interface (proprietary scripts kept local)
```

## 🎨 Frontend Component Map

```
src/frontend/src/
├── app/
│   ├── page.tsx                      # chat shell + SSE client parser
│   └── api/chat/stream/route.ts      # SSE proxy with keepalive
└── components/
    ├── message-bubble.tsx            # Fast/Full/Highlights tabs, Rx card, markdown, ASCII
    ├── trust-gauges.tsx              # trust score radar
    ├── reference-sidebar.tsx         # clickable, verified citations
    ├── knowledge-graph.tsx           # Neo4j graph view (@xyflow/react)
    ├── decision-tree-viewer.tsx      # agent reasoning tree
    ├── trend-monitor.tsx             # lab value trends (recharts)
    ├── reports/episodes-knowledge-graph.tsx
    ├── chat-input.tsx                # auto-grow textarea + voice
    └── ui/                           # logo, badges, shimmer, voice-morph…
```

## 🧰 Extending the System

### ➕ Add a council agent
1. `src/backend/agents/myagent.py` → subclass `BaseAgent`, set `model` & `max_tokens`.
2. Give it an `analyze_for_council(...)` (or similar) coroutine returning a dict.
3. Register it in `orchestrator.py`'s `agent_map` with a `phase` label.
4. Add any new fields to `api/schemas.py` (`ChatResponse`).
5. Render them in `components/message-bubble.tsx`.

### ➕ Add an MCP data source
1. Add a service to `docker-compose.yml` using `node:20-slim` + `mcp-http-bridge.mjs`.
2. Add a `tools/myservice_mcp.py` HTTP client.
3. Call it from the Research or Drug agent.
4. Add the URL to `core/config.py` + `.env.example`.

### ➕ Add an EHR
See the dedicated guide → [`EHR_ADAPTER.md`](./EHR_ADAPTER.md).

## 💻 Local Development without Docker

```bash
# ── Backend ──
cd /path/to/cerebralink
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r src/backend/requirements.txt
export $(grep -v '^#' .env | xargs)        # load env
PYTHONPATH=. uvicorn src.backend.api.app:app --reload --port 8000

# ── Frontend ──
cd src/frontend
npm install
BACKEND_URL=http://localhost:8000 npm run dev   # → http://localhost:3000
```

You'll still want Redis and Neo4j running (e.g. `docker compose up -d redis neo4j`),
and at least the MCP sidecars you intend to query.
