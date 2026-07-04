import os
import asyncio
import json
import typer
from typing import Optional

from app.cli.client import DevLensClient
from app.cli.exceptions import LocalAuditError
from app.cli.output import render_score_card, render_rules_table, render_recommendations, render_narrative_panel
from app.cli.formatter import get_console

# Typer command handler
def audit(
    repo_or_path: str = typer.Argument(..., help="GitHub Repository URL (online) or Local Directory Path (offline)."),
    offline: bool = typer.Option(False, "--offline", "-o", help="Inspect local repository offline using built-in engine."),
    json_format: bool = typer.Option(False, "--json", help="Print audit results as raw JSON."),
    markdown_format: bool = typer.Option(False, "--markdown", help="Print audit results in Markdown format."),
    html_format: bool = typer.Option(False, "--html", help="Print audit results in HTML format."),
    score_only: bool = typer.Option(False, "--score-only", help="Print ONLY the final overall score float.")
):
    """Analyze repository code quality, framework configurations, and security compliance."""
    console = get_console()

    # Determine if we should force offline based on path vs URL
    is_url = repo_or_path.startswith("http://") or repo_or_path.startswith("https://") or "github.com" in repo_or_path
    
    if offline or (not is_url and os.path.isdir(repo_or_path)):
        # Run local offline audit
        report = run_offline_audit(repo_or_path)
    else:
        # Run online API audit
        if not is_url:
            typer.echo("Error: Online audits require a valid GitHub repository URL. Did you mean to use '--offline'?")
            raise typer.Exit(code=1)
        report = run_online_audit(repo_or_path)

    # Process scorecards
    scorecard = report.get("scorecard", {})
    score = scorecard.get("overall_score", 0.0)
    
    if score_only:
        console.print(f"{score:.1f}")
        return

    if json_format:
        console.print_json(json.dumps(report))
        return

    if markdown_format:
        # Simple Markdown output
        markdown_str = f"# DevLens Audit Report: {report.get('metadata', {}).get('repo_name', 'Repository')}\n\n"
        markdown_str += f"## Score: {score:.1f}/10.0\n"
        markdown_str += f"**Scoring Version**: {scorecard.get('scoring_version', 'N/A')}\n\n"
        markdown_str += "### Rule Results:\n"
        for rule in scorecard.get("rule_results", []):
            passed = "PASSED" if rule.get("passed") else "FAILED"
            markdown_str += f"- **{rule.get('rule_id')}**: {rule.get('description')} -> *{passed}* ({rule.get('points_awarded')}/{rule.get('max_points')} pts)\n"
        console.print(markdown_str)
        return

    if html_format:
        # Simple HTML output
        html_str = f"<h1>DevLens Audit Report</h1><p>Score: <strong>{score:.1f}/10.0</strong></p>"
        html_str += "<ul>"
        for rule in scorecard.get("rule_results", []):
            passed = "Passed" if rule.get("passed") else "Failed"
            html_str += f"<li>{rule.get('rule_id')}: {rule.get('description')} - {passed}</li>"
        html_str += "</ul>"
        console.print(html_str)
        return

    # Default: Rich styled layout
    metadata = report.get("metadata", {})
    execution = report.get("execution", {})
    
    # 1. Print scorecard
    status = "completed" if execution.get("scoring_completed") else "failed"
    render_score_card(score, status, int(report.get("duration_ms", 0)))
    
    # 2. Print rule results
    render_rules_table(scorecard.get("rule_results", []))
    
    # 3. Print narrative summaries if present
    narrative = report.get("narrative")
    if narrative:
        render_narrative_panel(
            narrative.get("summary", ""),
            narrative.get("recruiter_verdict", ""),
            narrative.get("maturity_estimate", "Intermediate")
        )
        
        # 4. Print recommendations
        render_recommendations(narrative.get("recommendations", []))

def run_offline_audit(path: str) -> dict:
    """Execute local repository scan and pipeline evaluation."""
    from app.models.github import RepositorySnapshot
    from app.rie.pipeline import AuditPipeline
    import time
    
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        raise LocalAuditError(f"Local repository path '{path}' does not exist.")

    files = []
    raw_files_content = {}
    readme_content = ""

    # Traversal loop
    for root, dirs, filenames in os.walk(abs_path):
        # Exclude common build artifacts and configuration dirs
        dirs[:] = [d for d in dirs if d not in (".git", "node_modules", "venv", ".venv", "__pycache__", "dist", "build", ".gemini")]
        
        for filename in filenames:
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, abs_path).replace("\\", "/")
            
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                files.append(rel_path)
                raw_files_content[rel_path] = content
                
                # README mapping
                if filename.lower() in ("readme.md", "readme.txt", "readme"):
                    readme_content = content
            except Exception:
                pass

    snapshot = RepositorySnapshot(
        name=os.path.basename(abs_path) or "local-repo",
        readme=readme_content,
        files=files,
        raw_files_content=raw_files_content
    )

    start_time = time.time()
    pipeline = AuditPipeline(ai_provider=None) # No AI provider -> deterministic offline mode
    
    # Run async pipeline synchronously
    report = asyncio.run(pipeline.execute_audit(snapshot))
    duration_ms = int((time.time() - start_time) * 1000)

    # Convert Pydantic models to dict matching API structures using JSON serialization to safely map datetimes
    report_json_str = report.model_dump_json() if hasattr(report, "model_dump_json") else report.json()
    report_dict = json.loads(report_json_str)

    report_dict["analysis"] = {}
    report_dict["duration_ms"] = duration_ms

    return report_dict

def run_online_audit(repo_url: str) -> dict:
    """Trigger remote audit flow on FastAPI backend."""
    client = DevLensClient()
    payload = {"repo_url": repo_url}
    
    # Call public POST /analyze endpoint
    response = client.request("POST", "analyze", json_data=payload)
    
    # Structure online report return format
    return {
        "metadata": response.get("metadata", {}),
        "scorecard": response.get("scorecard", {}),
        "narrative": response.get("narrative"),
        "execution": response.get("execution", {}),
        "duration_ms": response.get("duration_ms", 1500)
    }
