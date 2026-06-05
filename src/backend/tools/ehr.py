"""EHR adapter selector.

Exposes a single ``auto_fetch_patient`` chosen by the ``EHR_ADAPTER`` env var
(see ``core/config.py``):

  * ``file``     (default) → file_adapter.py — synthetic/local JSON, runs on a fresh clone
  * ``cerebral``           → cerebral.py — Acıbadem CerebralPlus; requires the
                              git-ignored ``scripts/cerebral_*.py`` scraper scripts

The orchestrator imports ``auto_fetch_patient`` from here, so swapping adapters is
a one-line env change rather than a code edit.
"""

from __future__ import annotations

import logging

from src.backend.core.config import settings

log = logging.getLogger("cerebralink.ehr")

if settings.ehr_adapter == "cerebral":
    from src.backend.tools.cerebral import auto_fetch_patient
    log.info("EHR adapter: cerebral (Acıbadem CerebralPlus)")
else:
    from src.backend.tools.file_adapter import auto_fetch_patient
    log.info("EHR adapter: file (synthetic/local JSON)")

__all__ = ["auto_fetch_patient"]
