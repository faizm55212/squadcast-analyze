from future import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Dict

def utc_stamp() -> str:
return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def ensure_dirs():
Path("data/raw").mkdir(parents=True, exist_ok=True)
Path("data/processed").mkdir(parents=True, exist_ok=True)
Path("config").mkdir(parents=True, exist_ok=True)

def save_bytes(content: bytes, path: Path) -> Path:
path.parent.mkdir(parents=True, exist_ok=True)
path.write_bytes(content)
return path

def load_json_records(path: Path) -> List[Dict[str, Any]]:
data = json.loads(path.read_text(encoding="utf-8"))
if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
return data["data"]
if isinstance(data, list):
return data
return [data]
