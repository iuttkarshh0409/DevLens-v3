from importlib.metadata import PackageNotFoundError, version as package_version
from pathlib import Path
import tomllib

import typer
from app.cli.client import DevLensClient
from app.cli.commands.config import get_active_config


def get_cli_version() -> str:
    try:
        installed_version = package_version("devlens")
        if installed_version:
            return installed_version
    except PackageNotFoundError:
        pass

    pyproject_path = Path(__file__).resolve().parents[3] / "pyproject.toml"
    with pyproject_path.open("rb") as pyproject_file:
        pyproject = tomllib.load(pyproject_file)
    return pyproject["project"]["version"]

def version():
    """Display the active CLI, connected Server, and API version info."""
    cfg = get_active_config()
    endpoint = cfg["endpoint"]
    cli_version = get_cli_version()
    
    # Query server health info
    client = DevLensClient()
    try:
        health_data = client.request("GET", "health")
        server_ver = health_data.get("service", "DevLens Backend")
        # Let's map standard backend version for display
        server_display = f"{server_ver} {cli_version}"
    except Exception:
        server_display = "Unreachable / Unknown"

    version_str = (
        f"DevLens CLI {cli_version}\n\n"
        "Server:\n"
        f"{server_display}\n\n"
        "API:\n"
        "v1\n\n"
        "Connected:\n"
        f"{endpoint}"
    )
    typer.echo(version_str)
