"""File-based EHR adapter — the default, dependency-free reference adapter.

Resolves a patient/protocol identifier to the normalized patient dict documented
in ``docs/EHR_ADAPTER.md`` ("Example B — Local file / CSV export") by reading a
checked-in or locally-exported JSON file. Unlike ``cerebral.py`` (which wraps the
git-ignored Acıbadem scraper scripts), this adapter runs on a fresh clone with no
credentials, no network, and no proprietary code — using synthetic data.

Lookup order for ``patient_<id>.json`` (first match wins):
  1. ``$PATIENT_DATA_DIR``            (Docker default: ``/app/patient_data``)
  2. ``<repo>/patient_data/``         (local exports — git-ignored)
  3. ``<repo>/``                      (where ``cerebral.py`` caches by default)
  4. ``<repo>/examples/``             (checked-in synthetic samples, e.g. DEMO)

Selected when ``EHR_ADAPTER=file`` (the default). See ``core/config.py``.
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[3]
EXAMPLES_DIR = PROJECT_ROOT / "examples"

log = logging.getLogger("cerebralink.file_adapter")


def _candidate_dirs() -> list[Path]:
    dirs: list[Path] = []
    env_dir = os.environ.get("PATIENT_DATA_DIR")
    if env_dir:
        dirs.append(Path(env_dir))
    dirs.append(PROJECT_ROOT / "patient_data")
    dirs.append(PROJECT_ROOT)
    dirs.append(EXAMPLES_DIR)
    # de-duplicate while preserving order
    seen: set[str] = set()
    out: list[Path] = []
    for d in dirs:
        key = str(d)
        if key not in seen:
            seen.add(key)
            out.append(d)
    return out


def _normalize_protocol_id(pid: str) -> str:
    """Strip spaces/dashes: '7352 4705' → '73524705'. Mirrors cerebral.py."""
    return re.sub(r"[\s\-]+", "", str(pid).strip())


def _resolve_path(protocol_id: str) -> Path | None:
    """Return the first existing patient_<id>.json across the candidate dirs."""
    pid = _normalize_protocol_id(protocol_id)
    for d in _candidate_dirs():
        p = d / f"patient_{pid}.json"
        if p.exists():
            return p
    return None


def patient_exists(protocol_id: str) -> bool:
    """True if a patient_<id>.json file exists in any candidate directory."""
    return _resolve_path(protocol_id) is not None


def load_cached_patient(protocol_id: str) -> dict[str, Any]:
    """Load patient_<id>.json from the first candidate directory that has it."""
    path = _resolve_path(protocol_id)
    if path is None:
        raise FileNotFoundError(f"No patient_{_normalize_protocol_id(protocol_id)}.json found")
    return json.loads(path.read_text(encoding="utf-8"))


async def load_patient_from_file(path: str) -> dict[str, Any]:
    """Load an already-exported patient JSON file by explicit path."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


async def fetch_patient(patient_id: str, auth: str = "") -> dict[str, Any]:
    """No network for the file adapter — this is just the local load."""
    return load_cached_patient(patient_id)


async def auto_fetch_patient(protocol_id: str) -> dict[str, Any]:
    """Resolve an identifier to the normalized patient dict from a JSON file.

    Try ``patient_DEMO.json`` to see the end-to-end flow on a fresh clone::

        # works out of the box (reads examples/patient_DEMO.json)
        ask CerebraLink:  "DEMO  what is the paracetamol dose for this patient?"

    To use your own (synthetic) patient, drop ``patient_<id>.json`` into
    ``patient_data/`` (git-ignored) following the shape in docs/EHR_ADAPTER.md.
    """
    pid = _normalize_protocol_id(protocol_id)
    path = _resolve_path(pid)
    if path is None:
        searched = ", ".join(str(d) for d in _candidate_dirs())
        raise FileNotFoundError(
            f"No patient file 'patient_{pid}.json' found (searched: {searched}).\n"
            f"The default file adapter needs a synthetic JSON file. Copy the bundled "
            f"sample to make it resolvable, e.g.:\n"
            f"    mkdir -p patient_data && cp examples/patient_DEMO.json patient_data/patient_{pid}.json\n"
            f"or try the id 'DEMO' (examples/patient_DEMO.json ships with the repo). "
            f"To use the Acıbadem scraper instead, set EHR_ADAPTER=cerebral (requires the "
            f"git-ignored scripts/cerebral_*.py)."
        )
    log.info("Loaded patient %s from %s", pid, path)
    return json.loads(path.read_text(encoding="utf-8"))
