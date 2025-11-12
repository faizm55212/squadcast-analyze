from __future__ import annotations
import requests


def get_access_token(refresh_token: str, auth_url: str, timeout: int = 60) -> str:
    """
    Exchange refresh token (via header X-Refresh-Token) for an access token.

    Supports both response shapes:
      1) {"access_token": "...", ...}
      2) {"data": {"access_token": "...", ...}}
    """
    resp = requests.get(
        auth_url,
        headers={"X-Refresh-Token": refresh_token},
        timeout=timeout,
    )
    resp.raise_for_status()
    payload = resp.json()

    # Try top-level first
    token = payload.get("access_token")
    if not token:
        # Try nested under "data"
        data = payload.get("data") or {}
        token = data.get("access_token")

    if not token:
        # Keep a short, safe preview for debugging—avoid dumping full JSON with secrets
        raise RuntimeError(
            "Missing access_token in response (expected 'access_token' or 'data.access_token'). "
            f"Keys at top-level: {list(payload.keys())}"
        )

    return token
