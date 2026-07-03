from typing import Dict, Any, List
from app.github.client import GitHubClient
from app.models.analysis import RepositoryAnalysis
from app.services.annotation_engine import RepositoryAnnotationEngine, RepositoryAnnotation

class ChecksService:
    def __init__(self, client: GitHubClient):
        self.client = client

    async def create_initial_check(self, owner: str, repo: str, head_sha: str) -> int:
        """Initiates a Check Run in 'in_progress' state and returns its check_run_id."""
        payload = {
            "name": "DevLens Code Audit",
            "head_sha": head_sha,
            "status": "in_progress",
            "started_at": self._now_iso(),
            "output": {
                "title": "DevLens Audit Running",
                "summary": "Analyzing repository files and configuration..."
            }
        }
        res = await self.client.create_check_run(owner, repo, payload)
        return res.get("id")

    async def complete_check(
        self,
        owner: str,
        repo: str,
        check_run_id: int,
        analysis: RepositoryAnalysis,
        score: float,
        raw_files: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Updates the Check Run with completion stats, Markdown reports, and annotations."""
        # Calculate conclusion
        conclusion = "success" if score >= 7.0 else "failure"

        # Generate annotations
        annotations = RepositoryAnnotationEngine.generate_annotations(analysis, raw_files)

        # Build output details
        summary = f"### DevLens Audit Score: **{score:.1f}/10.0**\n\n"
        summary += f"Resulting status: **{conclusion.upper()}** (Requires score >= 7.0 to pass)\n"
        
        # Split annotations: repository level in description, file/line in github annotation object
        github_annotations = []
        repo_warnings = []

        for ann in annotations:
            if ann.level == "repository":
                repo_warnings.append(f"- **{ann.message}**: {ann.suggestion}")
            else:
                # File/line annotations mapped to GitHub structure
                path = ann.path if ann.path else "README.md"  # Default fallback path
                start_line = ann.start_line if ann.start_line else 1
                end_line = ann.end_line if ann.end_line else 1
                
                github_annotations.append({
                    "path": path,
                    "start_line": start_line,
                    "end_line": end_line,
                    "annotation_level": "warning",
                    "title": ann.message,
                    "message": ann.suggestion
                })
                
        # Sort deterministically to ensure stable Check Run outputs
        github_annotations.sort(key=lambda x: (x["path"], x["start_line"], x["title"]))

        # Partition annotations into batches of 50
        batches = [github_annotations[i:i + 50] for i in range(0, len(github_annotations), 50)]
        first_annotations = batches[0] if batches else []

        text_body = ""
        if repo_warnings:
            text_body += "#### Repository-Level Suggestions:\n" + "\n".join(repo_warnings) + "\n\n"
        
        text_body += "#### Scoring Breakdown:\n"
        for name, result in analysis.results.items():
            status_icon = "✔" if result.passed else "✘"
            text_body += f"- {status_icon} **{name}**: {'Passed' if result.passed else 'Failed'}\n"

        # Publish the first batch in the complete check run payload
        payload = {
            "status": "completed",
            "completed_at": self._now_iso(),
            "conclusion": conclusion,
            "output": {
                "title": f"DevLens Audit Score: {score:.1f}/10.0",
                "summary": summary,
                "text": text_body,
                "annotations": first_annotations
            }
        }
        res = await self.client.update_check_run(owner, repo, check_run_id, payload)

        # Patch remaining batches sequentially
        if len(batches) > 1:
            for idx, batch in enumerate(batches[1:]):
                try:
                    patch_payload = {
                        "output": {
                            "title": f"DevLens Audit Score: {score:.1f}/10.0",
                            "summary": f"Additional audit annotations (Batch {idx + 2} of {len(batches)})",
                            "annotations": batch
                        }
                    }
                    await self.client.update_check_run(owner, repo, check_run_id, patch_payload)
                except Exception as e:
                    logger.error(f"Partial upload failure for annotation batch {idx + 2}: {str(e)}")

        return res

    def _now_iso(self) -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
