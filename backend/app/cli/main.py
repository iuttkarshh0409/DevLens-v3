import typer
import sys
from typing import Optional

from app.cli.exceptions import CLIException

# Main Typer App
app = typer.Typer(
    name="devlens",
    help="Official DevLens CLI for repository auditing, auth management, and historical analytics.",
    no_args_is_help=True
)

# Global options Callback
@app.callback()
def main_callback(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable detailed logging output.")
):
    """DevLens CLI - Inspect code quality, run security audits, and fetch repository analytics."""
    # Stash verbose flag in state if needed
    pass

# Import command groups to register them
from app.cli.commands.config import config_app
from app.cli.commands.analytics import analytics_app
from app.cli.commands.cache import cache_app
from app.cli.commands.auth import login, logout, whoami
from app.cli.commands.audit import audit
from app.cli.commands.version import version

# Register command groups (Sub-commands)
app.add_typer(config_app, name="config", help="Manage DevLens CLI configuration files.")
app.add_typer(analytics_app, name="analytics", help="Retrieve repository health and historical trends.")
app.add_typer(cache_app, name="cache", help="Query and invalidate active cache layers.")

# Register direct commands
app.command(name="login", help="Authenticate with the DevLens API using a Personal Access Token.")(login)
app.command(name="logout", help="Log out and clear active credentials.")(logout)
app.command(name="whoami", help="Check active session authentication details.")(whoami)
app.command(name="audit", help="Run repository intelligence and code quality audits (online or offline).")(audit)
app.command(name="version", help="Display the active CLI, Server, and API version information.")(version)

# Error handling wrapper
def run():
    try:
        app()
    except CLIException as e:
        # Write formatted error to stderr and exit with code
        sys.stderr.write(f"Error: {e.message}\n")
        sys.exit(e.exit_code)
    except Exception as e:
        sys.stderr.write(f"Unexpected Error: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    run()
