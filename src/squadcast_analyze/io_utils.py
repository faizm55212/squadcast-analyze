from __future__ import annotations
import os
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List


# ----------------------------------------------------------------------
# basic I/O utilities
# ----------------------------------------------------------------------

def ensure_dirs() -> None:
    """
    Ensure the data/raw and data/processed directories exist.
    """
    for sub in ("data/raw", "data/processed"):
        Path(sub).mkdir(parents=True, exist_ok=True)


def utc_stamp() -> str:
    """
    Returns a UTC timestamp string (e.g. 20251112T140906Z)
    """
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def save_bytes(content: bytes | str, path: Path) -> None:
    """
    Save bytes (or text) to file.
    """
    if isinstance(content, str):
        content = content.encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)


def load_json_records(path: Path) -> List[Dict[str, Any]]:
    """
    Load incidents from JSON file, handling common envelopes:
      - {"data": [...]}
      - {"incidents": [...]}
      - {"results": [...]}
      - {"items": [...]}
      - {"records": [...]}
    If it's already a list, return as-is. Otherwise, wrap single dict.
    """
    data = json.loads(path.read_text(encoding="utf-8"))

    # 1) List at top-level
    if isinstance(data, list):
        return data

    # 2) Dict with a known list key
    if isinstance(data, dict):
        for key in ("data", "incidents", "results", "items", "records"):
            val = data.get(key)
            if isinstance(val, list):
                return val

        # 3) Dict with exactly one key whose value is a list
        if len(data) == 1:
            only_val = next(iter(data.values()))
            if isinstance(only_val, list):
                return only_val

    # 4) Fallback: wrap as single record
    return [data]
