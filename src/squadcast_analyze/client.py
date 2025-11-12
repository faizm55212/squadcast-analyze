from future import annotations
from dataclasses import dataclass
from typing import Literal
import requests

@dataclass
class SquadcastClient:
base_api: str
access_token: str
timeout: int = 120

def export_incidents(
    self,
    start_iso: str,
    end_iso: str,
    owner_id: str,
    export_type: Literal["json", "csv"] = "json",
) -> bytes:
    url = (
        f"{self.base_api.rstrip('/')}/incidents/export"
        f"?type={export_type}&start_time={start_iso}&end_time={end_iso}&owner_id={owner_id}"
    )
    headers = {
        "Authorization": f"Bearer {self.access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json" if export_type == "json" else "text/csv",
    }
    r = requests.get(url, headers=headers, timeout=self.timeout)
    if r.status_code != 200:
        raise RuntimeError(f"Error {r.status_code}: {r.text[:4000]}")
    return r.content


