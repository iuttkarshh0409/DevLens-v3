import os
import typer
import tomllib
from typing import Dict, Any

from app.cli.exceptions import ConfigurationError

# Default Constants
DEFAULT_CONFIG_DIR = os.path.expanduser("~/.devlens")
DEFAULT_CONFIG_PATH = os.path.join(DEFAULT_CONFIG_DIR, "config.toml")

DEFAULT_DEFS = {
    "endpoint": "http://localhost:8000",
    "token": "",
    "format": "rich",
    "timeout": 30,
    "organization": "",
    "installation_id": 0
}

# Typer Config Router
config_app = typer.Typer(no_args_is_help=True)

def dict_to_toml(d: dict) -> str:
    """Helper to serialize a single level dict into TOML format."""
    lines = []
    for k, v in d.items():
        if isinstance(v, bool):
            lines.append(f"{k} = {str(v).lower()}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k} = {v}")
        elif isinstance(v, str):
            escaped = v.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{k} = "{escaped}"')
        elif v is None:
            lines.append(f'{k} = ""')
    return "\n".join(lines) + "\n"

def load_file_config() -> Dict[str, Any]:
    """Load configuration dictionary from the config.toml file."""
    config_path = os.getenv("DEVLENS_CONFIG", DEFAULT_CONFIG_PATH)
    if not os.path.exists(config_path):
        return {}
    try:
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        raise ConfigurationError(f"Failed to parse config file: {str(e)}")

def write_file_config(config_data: Dict[str, Any]) -> None:
    """Save configuration dictionary back to the config.toml file."""
    config_path = os.getenv("DEVLENS_CONFIG", DEFAULT_CONFIG_PATH)
    config_dir = os.path.dirname(config_path)
    try:
        os.makedirs(config_dir, exist_ok=True)
        toml_str = dict_to_toml(config_data)
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(toml_str)
    except Exception as e:
        raise ConfigurationError(f"Failed to write config file: {str(e)}")

def get_active_config(
    cli_endpoint: str = None,
    cli_token: str = None,
    cli_format: str = None,
    cli_timeout: int = None
) -> Dict[str, Any]:
    """
    Resolve config values based on precedence:
    1. CLI parameters (passed explicitly)
    2. Environment variables
    3. TOML configuration file
    4. Default definitions
    """
    file_cfg = load_file_config()
    
    # 1. Resolve Endpoint
    endpoint = cli_endpoint
    if not endpoint:
        endpoint = os.getenv("DEVLENS_ENDPOINT")
    if not endpoint:
        endpoint = file_cfg.get("endpoint")
    if not endpoint:
        endpoint = DEFAULT_DEFS["endpoint"]

    # 2. Resolve Token
    token = cli_token
    if not token:
        token = os.getenv("DEVLENS_TOKEN")
    if not token:
        raw_token = file_cfg.get("token")
        if raw_token:
            from app.cli.security import decrypt_token
            token = decrypt_token(raw_token)
            # Auto-migrate legacy plaintext tokens to Fernet encrypted format
            if not raw_token.startswith("enc:"):
                from app.cli.security import encrypt_token
                file_cfg["token"] = encrypt_token(raw_token)
                try:
                    write_file_config(file_cfg)
                except Exception:
                    pass
    if not token:
        token = DEFAULT_DEFS["token"]

    # 3. Resolve Format
    out_format = cli_format
    if not out_format:
        out_format = os.getenv("DEVLENS_FORMAT")
    if not out_format:
        out_format = file_cfg.get("format")
    if not out_format:
        out_format = DEFAULT_DEFS["format"]

    # 4. Resolve Timeout
    timeout = cli_timeout
    if not timeout:
        env_timeout = os.getenv("DEVLENS_TIMEOUT")
        if env_timeout:
            try:
                timeout = int(env_timeout)
            except ValueError:
                pass
    if not timeout:
        timeout = file_cfg.get("timeout")
    if not timeout:
        timeout = DEFAULT_DEFS["timeout"]

    # 5. Organization & Installation ID
    org = os.getenv("DEVLENS_ORGANIZATION") or file_cfg.get("organization") or DEFAULT_DEFS["organization"]
    inst_id = file_cfg.get("installation_id") or DEFAULT_DEFS["installation_id"]
    env_inst = os.getenv("DEVLENS_INSTALLATION_ID")
    if env_inst:
        try:
            inst_id = int(env_inst)
        except ValueError:
            pass

    return {
        "endpoint": endpoint,
        "token": token,
        "format": out_format,
        "timeout": int(timeout),
        "organization": org,
        "installation_id": int(inst_id)
    }

@config_app.command(name="init")
def config_init():
    """Initialize a default config.toml file."""
    config_path = os.getenv("DEVLENS_CONFIG", DEFAULT_CONFIG_PATH)
    if os.path.exists(config_path):
        typer.echo(f"Configuration file already exists at {config_path}")
        return
    write_file_config(DEFAULT_DEFS)
    typer.echo(f"Initialized configuration file at {config_path}")

@config_app.command(name="show")
def config_show():
    """Display the active configuration parameters."""
    cfg = get_active_config()
    typer.echo("Active DevLens CLI Configuration:")
    for k, v in cfg.items():
        # Mask credentials
        val = "********" if k == "token" and v else v
        typer.echo(f"  {k}: {val}")

@config_app.command(name="set")
def config_set(
    key: str = typer.Argument(..., help="Config key: endpoint, token, format, timeout, organization, or installation_id"),
    value: str = typer.Argument(..., help="The value to assign to the configuration key")
):
    """Assign a value to a configuration key in the TOML file."""
    file_cfg = load_file_config()
    
    # Merge defaults for missing values
    merged = {**DEFAULT_DEFS, **file_cfg}
    
    if key not in merged:
        typer.echo(f"Error: Unknown configuration key '{key}'.")
        raise typer.Exit(code=1)
        
    # Cast variables properly
    if key == "timeout" or key == "installation_id":
        try:
            merged[key] = int(value)
        except ValueError:
            typer.echo(f"Error: Configuration key '{key}' must be an integer.")
            raise typer.Exit(code=1)
    elif key == "token":
        from app.cli.security import encrypt_token
        merged[key] = encrypt_token(value)
    else:
        merged[key] = value
        
    write_file_config(merged)
    typer.echo(f"Updated configuration parameter '{key}' successfully.")
