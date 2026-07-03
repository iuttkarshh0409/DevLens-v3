from typing import Dict, Any
from app.github.client import GitHubClient

class StatusService:
    def __init__(self, client: GitHubClient):
        self.client = client

    async def post_pending_status(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        """Publishes a pending commit status indicating analysis has started."""
        payload = {
            "state": "pending",
            "description": "DevLens audit is running...",
            "context": "devlens/audit"
        }
        return await self.client.post_commit_status(owner, repo, sha, payload)

    async def post_completion_status(self, owner: str, repo: str, sha: str, score: float) -> Dict[str, Any]:
        """Publishes the final status based on the audit score (>= 7.0 is success)."""
        is_success = score >= 7.0
        state = "success" if is_success else "failure"
        description = f"DevLens audit score: {score:.1f}/10.0 ({'PASSED' if is_success else 'FAILED'})"
        
        # Link back to dashboard/UI
        target_url = "https://dev-lens-lime.vercel.app"

        payload = {
            "state": state,
            "target_url": target_url,
            "description": description,
            "context": "devlens/audit"
        }
        return await self.client.post_commit_status(owner, repo, sha, payload)
