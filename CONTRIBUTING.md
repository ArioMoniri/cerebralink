<div align="center">

# 🧠 Contributing to CerebraLink

_Thank you for helping build safer, faster clinical decision support!_ 💙

</div>

---

We love contributions of every size — from fixing a typo to adding a whole new
data-source agent. This guide explains how to get set up, the standards we hold,
and how to land your change.

> [!IMPORTANT]
> **CerebraLink touches the clinical domain.** Read the
> [Clinical Safety Rules](#-clinical-safety-rules) and the
> [Code of Conduct](./CODE_OF_CONDUCT.md) before contributing. Never commit real
> patient data (PHI/PII) — use synthetic data only.

## 📋 Table of Contents

- [🚀 Quick Start (Dev Environment)](#-quick-start-dev-environment)
- [🧭 Ways to Contribute](#-ways-to-contribute)
- [🌳 Branch & Commit Conventions](#-branch--commit-conventions)
- [🎨 Code Style](#-code-style)
- [🧪 Testing & CI](#-testing--ci)
- [🩺 Clinical Safety Rules](#-clinical-safety-rules)
- [🔌 Adding a New Agent or Data Source](#-adding-a-new-agent-or-data-source)
- [🔁 Pull Request Checklist](#-pull-request-checklist)
- [🐛 Reporting Bugs](#-reporting-bugs)
- [💡 Proposing Features](#-proposing-features)

## 🚀 Quick Start (Dev Environment)

```bash
# 1. Fork & clone
git clone https://github.com/<your-username>/cerebralink.git
cd cerebralink

# 2. Copy the env template and add your API keys
cp .env.example .env
#   → set ANTHROPIC_API_KEY (required) and EXA_API_KEY (recommended)

# 3. Boot the full stack (frontend + backend + Redis + Neo4j + MCP sidecars)
docker compose up -d --build

# 4. Open the UI
open http://localhost:3100
```

Prefer running services natively? See [`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md#-local-development-without-docker).

## 🧭 Ways to Contribute

| Type | Examples |
|------|----------|
| 🐛 **Bug fixes** | SSE stream drops, parser edge-cases, UI glitches |
| 🤖 **New agents** | A nutrition agent, a radiology agent, a triage agent |
| 🔌 **New data sources** | Add an MCP sidecar, wire up a new guideline API |
| 🌍 **EHR adapters** | Implement an adapter for Epic, OpenEMR, FHIR, etc. (see [`docs/EHR_ADAPTER.md`](./docs/EHR_ADAPTER.md)) |
| 🧪 **Lab parsers** | Support new lab-report formats / languages |
| 🎨 **UI/UX** | Components, animations, accessibility, i18n |
| 📚 **Docs** | Tutorials, diagrams, translations |
| ⚡ **Performance** | Token reduction, caching, latency |

## 🌳 Branch & Commit Conventions

- Branch from `main`: `feat/<short-name>`, `fix/<short-name>`, `docs/<short-name>`.
- We follow **[Conventional Commits](https://www.conventionalcommits.org/)**:

```
feat(agents): add nutrition agent backed by USDA FoodData MCP
fix(lab-parser): handle serology reports with combined textual+numeric results
docs(readme): add Lottie embedding instructions
perf(composer): reduce fast-answer max_tokens to 3072
```

## 🎨 Code Style

### Python (backend)
- Python **3.12+**, fully type-hinted, `from __future__ import annotations`.
- Keep files **under 500 lines** (split into modules in `tools/` or `agents/`).
- Follow **Domain-Driven Design** — agents own behavior, `tools/` own I/O.
- Validate input at system boundaries; sanitize file paths.

### TypeScript (frontend)
- **Strict** TypeScript — `npx tsc --noEmit` must pass with zero errors.
- React function components + hooks. No class components.
- Use `Array.from(new Set(...))` (not spread) to stay ES2017-compatible.
- Tailwind for styling; keep the "liquid glass" design language consistent.

## 🧪 Testing & CI

Every PR runs three jobs (`.github/workflows/ci.yml`):

| Job | What it checks |
|-----|----------------|
| 🟦 **Frontend Build** | `npx tsc --noEmit` + `npm run build` |
| 🐍 **Backend Import Check** | All backend modules import cleanly |
| 🐳 **Docker Compose Validation** | `docker compose config` is valid |

Run them locally before pushing:

```bash
# Frontend
cd src/frontend && npx tsc --noEmit && npm run build

# Backend (from repo root)
pip install -r src/backend/requirements.txt
PYTHONPATH=. python -c "import src.backend.api.app"

# Compose
docker compose config --quiet
```

## 🩺 Clinical Safety Rules

> [!WARNING]
> These rules are **non-negotiable**. Violations are grounds for rejecting a PR.

1. **No real PHI/PII — ever.** Tests, fixtures, screenshots, and issues must use
   fully synthetic data.
2. **Preserve disclaimers.** Don't remove the decision-support framing or the
   "verify with a clinician" language from any output path.
3. **Citations must be verifiable.** New guideline/citation sources must return a
   real, resolvable URL. We verify links before display (see
   [`tools/reader_proxy.py`](./src/backend/tools/reader_proxy.py)).
4. **Dosing changes need a source.** Any change that affects drug dosing,
   interactions, or prescriptions must cite the guideline/label it's based on in
   the PR description.
5. **PHI masking stays on.** The `phi_masker` agent runs before patient data
   reaches any external LLM. Don't bypass it.

## 🔌 Adding a New Agent or Data Source

CerebraLink is a **multi-agent council**. To add an agent:

1. Create `src/backend/agents/<name>.py` subclassing `BaseAgent`.
2. Pick a model tier in `core/config.py` (`haiku` for cheap/simple,
   `sonnet`/`opus` for reasoning).
3. Register it in `core/orchestrator.py`'s `agent_map` with a `phase` label.
4. Expose any new response fields in `api/schemas.py`.
5. Render them in `src/frontend/src/components/message-bubble.tsx`.

To add an **external data source**, prefer an **MCP sidecar** (see
`docker-compose.yml` and `scripts/mcp-http-bridge.mjs`). Full walkthrough:
[`docs/ARCHITECTURE.md`](./docs/ARCHITECTURE.md#-extending-the-system).

## 🔁 Pull Request Checklist

- [ ] Branch named `feat/…`, `fix/…`, or `docs/…`
- [ ] Conventional Commit messages
- [ ] `npx tsc --noEmit` passes (frontend changes)
- [ ] Backend imports cleanly (backend changes)
- [ ] `docker compose config --quiet` passes (compose changes)
- [ ] No real PHI/PII anywhere in the diff
- [ ] Disclaimers & PHI masking preserved
- [ ] New citations resolve to real URLs
- [ ] Docs updated if behavior changed
- [ ] Linked the issue it closes (`Closes #123`)

## 🐛 Reporting Bugs

Open an issue using the **Bug Report** template. Include:
- Steps to reproduce (with **synthetic** data)
- Expected vs. actual behavior
- Service logs (`docker compose logs backend --tail 50`)
- Screenshots/screencasts where helpful

## 💡 Proposing Features

Open an issue using the **Feature Request** template. Describe the clinical or
developer problem, the proposed solution, and any alternatives. For large
features, please open a discussion first so we can align on design.

---

<div align="center">

**By contributing, you agree that your contributions will be licensed under the
[Apache License 2.0](./LICENSE).**

Made with 💙 for clinicians and engineers.

</div>
