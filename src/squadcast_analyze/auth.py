from future import annotations
import requests

def get_access_token(refresh_token: str, auth_url: str, timeout: int = 60) -> str:
"""
Exchange refresh token (via header X-Refresh-Token) for access token.
"""
resp = requests.get(auth_url, headers={"X-Refresh-Token": refresh_token}, timeout=timeout)
resp.raise_for_status()
data = resp.json()
token = data.get("access_token")
if not token:
raise RuntimeError(f"Missing access_token in response: {data}")
return token
