---
name: 🐛 Bug Report
about: Report a problem so we can fix it
title: "[Bug] "
labels: bug
assignees: ''
---

> ⚠️ **Never paste real patient data (PHI/PII).** Use synthetic data only.

## 🐛 Describe the bug
A clear and concise description of what the bug is.

## 🔁 To reproduce
Steps to reproduce the behavior (with **synthetic** data):
1. Go to '…'
2. Ask '…'
3. See error

## ✅ Expected behavior
What you expected to happen.

## 🖥️ Environment
- OS:
- Docker / Compose version:
- Branch / commit:
- Which service(s): `frontend` / `backend` / MCP / Neo4j / Redis

## 📋 Logs
```
docker compose logs backend --tail 50
```

## 📸 Screenshots
If applicable, add screenshots (no PHI).

## 🩺 Clinical-safety impact?
Does this affect dosing, interactions, prescriptions, or citations? If yes, please
flag it as high priority.
