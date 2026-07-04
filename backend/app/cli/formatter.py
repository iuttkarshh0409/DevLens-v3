import sys
from rich.console import Console
from app.cli.commands.config import get_active_config

def get_console() -> Console:
    """
    Get a configured Rich Console instance.
    Automatically disables colors in non-interactive (CI) environments 
    or when explicit text/JSON output formats are requested.
    """
    cfg = get_active_config()
    out_format = cfg.get("format", "rich")
    
    # Check if stdout is redirected or run in non-interactive shell
    is_interactive = sys.stdout.isatty()
    
    if not is_interactive or out_format in ("json", "csv", "markdown", "html"):
        return Console(color_system=None, force_terminal=False)
    return Console()
