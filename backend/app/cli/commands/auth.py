import typer
from typing import Optional

from app.cli.commands.config import load_file_config, write_file_config, get_active_config
from app.cli.client import DevLensClient
from app.cli.exceptions import AuthenticationError

def login(
    token: Optional[str] = typer.Option(None, "--token", "-t", help="Personal Access Token for verification.")
):
    """Authenticate with the DevLens API using a Personal Access Token (PAT)."""
    if not token:
        token = typer.prompt("Enter your Personal Access Token", hide_input=True)
        
    if not token:
        typer.echo("Error: Token cannot be empty.")
        raise typer.Exit(code=1)
        
    # Write token to file
    config_data = load_file_config()
    config_data["token"] = token
    write_file_config(config_data)
    
    # Verify token by checking health endpoint
    client = DevLensClient(token=token)
    try:
        health_data = client.request("GET", "health")
        typer.echo(f"Successfully authenticated with Server ({health_data.get('service', 'DevLens')})")
    except Exception as e:
        typer.echo(f"Warning: Auth token saved, but server health check failed: {str(e)}")

def logout():
    """Clear active authentication token from config."""
    config_data = load_file_config()
    if "token" in config_data:
        config_data["token"] = ""
        write_file_config(config_data)
        typer.echo("Logged out successfully. Authentication credentials cleared.")
    else:
        typer.echo("You are not currently logged in.")

def whoami():
    """Query configuration and server status to show active credentials."""
    cfg = get_active_config()
    endpoint = cfg["endpoint"]
    token = cfg["token"]
    
    if not token:
        typer.echo("Status: Not Authenticated (No token configured)")
        typer.echo(f"Endpoint: {endpoint}")
        return
        
    client = DevLensClient()
    try:
        health_data = client.request("GET", "health")
        server_status = f"Healthy ({health_data.get('service')})"
    except Exception:
        server_status = "Unreachable"
        
    typer.echo("Active Session Details:")
    typer.echo(f"  Endpoint: {endpoint}")
    typer.echo(f"  Token:    PAT (configured)")
    typer.echo(f"  Server:   {server_status}")
