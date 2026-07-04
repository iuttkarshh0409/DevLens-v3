import json
import csv
import typer
from typing import Optional

from app.cli.client import DevLensClient
from app.cli.commands.config import get_active_config
from app.cli.formatter import get_console

# Analytics Sub-Typer Group
analytics_app = typer.Typer(no_args_is_help=True)

@analytics_app.command(name="overview")
def analytics_overview(
    installation_id: Optional[int] = typer.Option(None, "--installation-id", "-i", help="GitHub App installation ID.")
):
    """Retrieve aggregated overview metrics for the organization."""
    console = get_console()
    cfg = get_active_config()
    inst_id = installation_id or cfg.get("installation_id") or 12345
    
    client = DevLensClient()
    response = client.request("GET", "api/v1/analytics/overview", params={"installation_id": inst_id})
    
    if cfg.get("format") == "json":
        console.print_json(json.dumps(response))
        return
        
    console.print(f"[bold cyan]DevLens Telemetry Overview Summary[/bold cyan]")
    console.print(f"  Total Repositories: [bold white]{response.get('total_repositories_monitored', 0)}[/bold white]")
    dist = response.get("score_distribution", {})
    console.print("  Score Distribution:")
    console.print(f"    High Quality (>=8.0): [green]{dist.get('high_quality', 0)}[/green]")
    console.print(f"    Medium Quality (5.0-7.9): [yellow]{dist.get('medium_quality', 0)}[/yellow]")
    console.print(f"    Low Quality (<5.0): [red]{dist.get('low_quality', 0)}[/red]")

@analytics_app.command(name="trends")
def analytics_trends(
    installation_id: Optional[int] = typer.Option(None, "--installation-id", "-i", help="GitHub App installation ID."),
    metric: str = typer.Option("score", "--metric", "-m", help="Metric to aggregate: score, security, documentation, testing"),
    period: str = typer.Option("weekly", "--period", "-p", help="Trend boundaries: daily, weekly, monthly")
):
    """Retrieve historical time-series analytics trends."""
    console = get_console()
    cfg = get_active_config()
    inst_id = installation_id or cfg.get("installation_id") or 12345
    
    client = DevLensClient()
    params = {"installation_id": inst_id, "metric": metric, "period": period}
    response = client.request("GET", "api/v1/analytics/trends", params=params)
    
    if cfg.get("format") == "json":
        console.print_json(json.dumps(response))
        return
        
    console.print(f"[bold cyan]Historical Trend Metrics ({period})[/bold cyan]")
    trends = response.get("trends", [])
    if not trends:
        console.print("  No time-series trend data available.")
        return
        
    for pt in trends:
        console.print(f"  - {pt.get('period_start')}: [bold white]{pt.get('value', 0.0):.2f}[/bold white] (based on {pt.get('audit_count')} audits)")

@analytics_app.command(name="repositories")
def analytics_repositories(
    installation_id: Optional[int] = typer.Option(None, "--installation-id", "-i", help="GitHub App installation ID."),
    page: int = typer.Option(1, "--page", help="Page index offset."),
    limit: int = typer.Option(10, "--limit", help="Number of records returned per page.")
):
    """Retrieve monitored repositories summary list."""
    console = get_console()
    cfg = get_active_config()
    inst_id = installation_id or cfg.get("installation_id") or 12345
    
    client = DevLensClient()
    params = {"installation_id": inst_id, "page": page, "limit": limit}
    response = client.request("GET", "api/v1/analytics/repositories", params=params)
    
    if cfg.get("format") == "json":
        console.print_json(json.dumps(response))
        return
        
    from rich.table import Table
    table = Table(title=f"Monitored Repositories (Page {page}/{((response.get('total_count', 0) - 1) // limit) + 1})")
    table.add_column("Repository ID", style="cyan")
    table.add_column("Repo Name", style="white")
    table.add_column("Health Score", style="bold green", justify="right")
    table.add_column("Last Audit", style="dim")
    table.add_column("Risk Level", style="bold red")

    for repo in response.get("data", []):
        score = repo.get("health_score", 0.0)
        score_style = "green" if score >= 8.0 else ("yellow" if score >= 5.0 else "red")
        
        table.add_row(
            repo.get("repository_id"),
            repo.get("repo_name"),
            f"[{score_style}]{score:.1f}[/{score_style}]",
            repo.get("last_audit", "")[:19],
            repo.get("risk_level", "medium").upper()
        )
    console.print(table)

@analytics_app.command(name="export")
def analytics_export(
    installation_id: Optional[int] = typer.Option(None, "--installation-id", "-i", help="GitHub App installation ID."),
    format_type: str = typer.Option("csv", "--format", "-f", help="Output format: csv or json"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="File path to write report to.")
):
    """Download and export analytics reports to files."""
    console = get_console()
    cfg = get_active_config()
    inst_id = installation_id or cfg.get("installation_id") or 12345
    
    client = DevLensClient()
    params = {"installation_id": inst_id, "format": format_type}
    response = client.request("GET", "api/v1/analytics/export", params=params)
    
    # Export payload is represented as raw rows or list of dictionary records
    if format_type.lower() == "json":
        out_content = json.dumps(response, indent=2)
    else:
        # Generate CSV contents locally from exported records if returned as dicts
        import io
        csv_file = io.StringIO()
        writer = csv.writer(csv_file)
        # Write headers
        writer.writerow(["Repository ID", "Repo Name", "Health Score", "Last Audit", "Risk Level"])
        for r in response.get("repositories", []):
            writer.writerow([
                r.get("repository_id"),
                r.get("repo_name"),
                r.get("health_score"),
                r.get("last_audit"),
                r.get("risk_level")
            ])
        out_content = csv_file.getvalue()
        
    if output:
        try:
            with open(output, "w", encoding="utf-8") as f:
                f.write(out_content)
            console.print(f"[green]Report exported to {output} successfully.[/green]")
        except Exception as e:
            typer.echo(f"Error writing file: {str(e)}")
            raise typer.Exit(code=1)
    else:
        console.print(out_content)
