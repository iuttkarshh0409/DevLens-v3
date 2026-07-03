from typing import Dict, Any, List
from app.github.client import GitHubClient
from app.models.analysis import RepositoryAnalysis
from app.services.annotation_engine import RepositoryAnnotationEngine

class PRReviewService:
    def __init__(self, client: GitHubClient):
        self.client = client

    async def submit_pr_review(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        analysis: RepositoryAnalysis,
        score: float,
        raw_files: Dict[str, str] = None
    ) -> Dict[str, Any]:
        """Analyzes a PR, detects potential regressions, and posts a review with comments."""
        annotations = RepositoryAnnotationEngine.generate_annotations(analysis, raw_files)
        
        # Determine review action & message
        is_passing = score >= 7.0
        event_action = "APPROVE" if is_passing else "REQUEST_CHANGES"
        
        review_body = f"### DevLens PR Code Audit: **{score:.1f}/10.0**\n\n"
        if is_passing:
            review_body += "✔ Repository meets the required quality bar (score >= 7.0). Great job!"
        else:
            review_body += "✘ Repository falls below the quality bar. Please resolve the comments below to merge."

        # Map file-level and line-level annotations to review comments
        comments = []
        for ann in annotations:
            if ann.level in ["file", "line"] and ann.path:
                line_no = ann.start_line if ann.start_line else 1
                comments.append({
                    "path": ann.path,
                    "line": line_no,
                    "body": f"**[{ann.message}]**\n{ann.suggestion}"
                })

        payload = {
            "body": review_body,
            "event": event_action,
            "comments": comments[:30]  # Limit to first 30 comments to avoid cluttering PR
        }
        return await self.client.create_pr_review(owner, repo, pull_number, payload)
