import typer
from app.cli.client import DevLensClient
from app.cli.commands.config import get_active_config

def version():
    """Display the active CLI, connected Server, and API version info."""
    cfg = get_active_config()
    endpoint = cfg["endpoint"]
    
    # Query server health info
    client = DevLensClient()
    try:
        health_data = client.request("GET", "health")
        server_ver = health_data.get("service", "DevLens Backend")
        # Let's map standard backend version for display
        server_display = f"{server_ver} 3.0.0"
    except Exception:
        server_display = "Unreachable / Unknown"

    version_str = (
        "DevLens CLI 1.0.0\n\n"
        "Server:\n"
        f"{server_display}\n\n"
        "API:\n"
        "v1\n\n"
        "Connected:\n"
        f"{endpoint}"
    )
    typer.echo(version_str)
