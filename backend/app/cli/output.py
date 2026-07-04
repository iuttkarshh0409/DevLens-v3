from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Group

from app.cli.formatter import get_console

def render_score_card(score: float, status: str, duration_ms: int):
    """Render a visual color-coded top scorecard panel."""
    console = get_console()
    
    if score >= 8.0:
        color = "green"
        verdict = "EXCELLENT"
    elif score >= 5.0:
        color = "yellow"
        verdict = "FAIR"
    else:
        color = "red"
        verdict = "RISKY"

    text = Text()
    text.append("Overall Score: ", style="bold white")
    text.append(f"{score:.1f}/10.0\n", style=f"bold {color}")
    text.append("Verdict: ", style="bold white")
    text.append(f"{verdict}\n", style=f"bold {color}")
    text.append("Status: ", style="bold white")
    text.append(f"{status.upper()}\n", style="bold cyan")
    text.append(f"Duration: {duration_ms} ms", style="dim italic")

    panel = Panel(
        text,
        title="[bold white]Audit Scorecard[/bold white]",
        border_style=color,
        padding=(1, 2)
    )
    console.print(panel)

def render_rules_table(rule_results: list):
    """Render table of checked rules."""
    console = get_console()
    table = Table(title="Rule Evaluations", expand=True)
    table.add_column("Rule ID", style="cyan", width=15)
    table.add_column("Description", style="white")
    table.add_column("Passed", style="bold", width=10)
    table.add_column("Points", justify="right", width=10)

    for r in rule_results:
        passed_text = "[green]YES[/green]" if r.get("passed", r.get("passed", False)) else "[red]NO[/red]"
        table.add_row(
            r.get("rule_id", ""),
            r.get("description", ""),
            passed_text,
            f"{r.get('points_awarded', 0):.1f}/{r.get('max_points', 0):.1f}"
        )
    console.print(table)

def render_recommendations(recommendations: list):
    """Render markdown-styled action items/recommendations."""
    console = get_console()
    if not recommendations:
        return
        
    table = Table(title="Prioritized Recommendations", expand=True)
    table.add_column("Title", style="bold yellow", width=25)
    table.add_column("Description", style="white")
    table.add_column("Impact", style="bold cyan", width=10)

    for rec in recommendations:
        table.add_row(
            rec.get("title", ""),
            rec.get("description", ""),
            rec.get("impact", "Low")
        )
    console.print(table)

def render_narrative_panel(summary: str, recruiter_verdict: str, maturity_estimate: str):
    """Render a text panel with narrative summaries and recruiter verdicts."""
    console = get_console()
    
    text = Text()
    text.append("[Maturity Level] ", style="bold cyan")
    text.append(f"{maturity_estimate}\n\n", style="bold white")
    text.append("[Summary]\n", style="bold yellow")
    text.append(f"{summary}\n\n", style="white")
    text.append("[Recruiter Verdict]\n", style="bold green")
    text.append(f"{recruiter_verdict}", style="white")

    panel = Panel(
        text,
        title="[bold white]AI Narrative Analysis[/bold white]",
        border_style="blue",
        padding=(1, 2)
    )
    console.print(panel)
