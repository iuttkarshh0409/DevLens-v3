import time
from typing import Dict, Any, Optional
from app.github.client import GitHubClient
from app.rie.pipeline import AuditPipeline
from app.ai.provider import GroqProvider

class AuditService:
    def __init__(self, fetcher: Optional[GitHubClient] = None, pipeline: Optional[AuditPipeline] = None):
        self.provider = GroqProvider()
        self.fetcher = fetcher or GitHubClient()
        self.pipeline = pipeline or AuditPipeline(ai_provider=self.provider)

    async def run_audit_flow(self, repo_url: str) -> Dict[str, Any]:
        # 1. Parse URL & Fetch raw metadata
        from app.github.parser import parse_github_url
        owner, repo = parse_github_url(repo_url)
        
        start_fetch = time.time()
        snapshot = await self.fetcher.fetch(owner, repo)
        fetch_time = (time.time() - start_fetch) * 1000.0

        # 2. Run Audit Pipeline
        start_pipeline = time.time()
        report = await self.pipeline.execute_audit(snapshot)
        pipeline_time = (time.time() - start_pipeline) * 1000.0

        # 3. Use mapper to return clean, typed legacy response
        from app.services.mapper import AuditResponseMapper
        return AuditResponseMapper.map_to_legacy_response(report, fetch_time, pipeline_time)
