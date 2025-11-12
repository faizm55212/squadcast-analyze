from future import annotations
from pathlib import Path
from typing import Optional
import typer
from tabulate import tabulate

from .config import load_settings
from .auth import get_access_token
from .client import SquadcastClient
from .io_utils import ensure_dirs, utc_stamp, save_bytes, load_json_records
from .analyzer import to_dataframe, top_counts

app = typer.Typer(help="Squadcast Analyze CLI - fetch & analyze incidents")

@app.command()
def auth(env_path: Optional[str] = typer.Option(".env", help="Path to .env")):
"""
Prints an access token (uses X-Refresh-Token flow).
"""
settings = load_settings(env_path)
token = get_access_token(settings.refresh_token, settings.auth_url)
typer.echo(token)

@app.command()
def fetch(
start: Optional[str] = typer.Option(None, help="ISO start time (UTC)"),
end: Optional[str] = typer.Option(None, help="ISO end time (UTC)"),
team: Optional[str] = typer.Option(None, help="Owner/team id (owner_id)"),
export_type: str = typer.Option("json", "--type", help="json or csv"),
env_path: Optional[str] = typer.Option(".env", help="Path to .env"),
):
"""
Fetch incidents (export) and save to data/raw.
"""
ensure_dirs()
settings = load_settings(env_path)

if export_type not in ("json", "csv"):
    raise typer.BadParameter("type must be 'json' or 'csv'")

start_iso = start or settings.default_start
end_iso = end or settings.default_end
owner_id = team or settings.team_id

if not start_iso or not end_iso:
    raise typer.BadParameter("Provide --start/--end or set START_TIME/END_TIME in .env")
if not owner_id:
    raise typer.BadParameter("Provide --team or set SQUADCAST_TEAM_ID in .env")

token = get_access_token(settings.refresh_token, settings.auth_url)
client = SquadcastClient(settings.base_api, token)

content = client.export_incidents(start_iso, end_iso, owner_id, export_type=export_type)
out = Path("data/raw") / (f"incidents_{utc_stamp()}.json" if export_type == "json" else f"incidents_{utc_stamp()}.csv")
save_bytes(content, out)
typer.secho(f"Saved: {out}", fg=typer.colors.GREEN)


@app.command()
def analyze(
input: str = typer.Option(..., help="Path to JSON exported file"),
group_by: str = typer.Option("service", help="Field to group by (e.g., service, environment, priority)"),
top: int = typer.Option(10, help="Top N"),
csv_out: Optional[str] = typer.Option(None, help="Optional CSV output"),
):
"""
Analyze Top-N counts grouped by any field (smart matching on nested columns).
"""
path = Path(input)
if not path.exists():
raise typer.BadParameter(f"Input not found: {path}")

records = load_json_records(path)
if not records:
    raise typer.BadParameter("No records to analyze.")

df = to_dataframe(records)
table = top_counts(df, group_by, top)

typer.echo(tabulate(table, headers="keys", tablefmt="github", showindex=False))

if csv_out:
    out_path = Path(csv_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(out_path, index=False)
    typer.secho(f"CSV saved: {out_path}", fg=typer.colors.GREEN)


