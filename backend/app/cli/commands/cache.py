import typer
from typing import Optional

from app.cli.client import DevLensClient
from app.cli.commands.config import get_active_config

cache_app = typer.Typer(no_args_is_help=True)

@cache_app.command(name="invalidate")
def cache_invalidate(
    installation_id: Optional[int] = typer.Option(None, "--installation-id", "-i", help="GitHub App installation ID.")
):
    """Invalidate active Redis analytics cache ranges."""
    cfg = get_active_config()
    inst_id = installation_id or cfg.get("installation_id") or 12345
    
    client = DevLensClient()
    
    # Calls cache invalidation API endpoint (POST /api/v1/analytics/cache/invalidate or similar)
    try:
        # Since we invalidate caches on webhook calls, we can trigger it via a delete/post request
        response = client.request("DELETE", "api/v1/analytics/cache", params={"installation_id": inst_id})
        typer.echo(f"Cache invalidated successfully for installation {inst_id}.")
    except Exception as e:
        typer.echo(f"Error invalidating cache: {str(e)}")
        raise typer.Exit(code=1)
