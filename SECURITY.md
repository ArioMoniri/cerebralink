# Security Policy

CerebraLink handles clinical data and connects to several third-party services.
We take security and patient-data safety seriously and appreciate responsible
disclosure.

## Reporting a vulnerability

Do **not** open a public issue for security problems. Instead:

- Email **moniriario@gmail.com** with details, or
- Use GitHub's [private vulnerability reporting](https://docs.github.com/en/code-security/security-advisories/guidance-on-reporting-and-writing-information-about-vulnerabilities/privately-reporting-a-security-vulnerability)
  ("Report a vulnerability" under the repository's **Security** tab).

Please include a description, reproduction steps (with **synthetic** data only —
never real PHI/PII), affected components, and any suggested remediation.

**Expected response:** acknowledgement within 7 days; a remediation plan or
assessment within 30 days. This is a single-maintainer project, so timelines are
best-effort.

## Scope

Security-relevant areas include:

- **PHI handling** — the regex de-identification pass (`agents/phi_masker.py`) and
  the patient-data ingestion/adapter path. Report any case where identifiers can
  reach an external model unmasked.
- **MCP sidecars** — several sidecars `npm install` packages at container startup
  (`docker-compose.yml`). Supply-chain or pinning concerns belong here. Pin and
  audit these images before any sensitive deployment.
- **Secrets handling** — `.env`, cookies, and patient exports are git-ignored;
  report any leak path that would commit them.
- **Outbound requests** — the reader proxy (`/api/reader`) and external API
  clients (Anthropic, Exa, MCP sidecars).

## Clinical-safety reports

A wrong drug dose, a dangerous interaction, or a hallucinated/incorrect citation
is a **clinical-safety** issue, not a code vulnerability — but we treat it as high
priority. Report these the same way (private email), labelled "clinical-safety".

## Supported versions

This is an early-stage (v0.x) research project. Only the `main` branch is
maintained; there are no backported security releases.
