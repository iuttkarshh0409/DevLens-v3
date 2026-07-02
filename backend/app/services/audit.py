import time
from typing import Dict, Any
from app.github.client import GitHubClient
from app.rie.pipeline import AuditPipeline
from app.ai.provider import GroqProvider

class AuditService:
    def __init__(self):
        self.fetcher = GitHubClient()
        self.provider = GroqProvider()
        self.pipeline = AuditPipeline(ai_provider=self.provider)

    async def run_audit_flow(self, repo_url: str) -> Dict[str, Any]:
        # 1. Parse URL & Fetch raw metadata
        from app.github.parser import parse_github_url
        owner, repo = parse_github_url(repo_url)
        
        start_fetch = time.time()
        repo_data = await self.fetcher.fetch(owner, repo)
        fetch_time = (time.time() - start_fetch) * 1000.0

        # 2. Run Audit Pipeline
        start_pipeline = time.time()
        report = await self.pipeline.execute_audit(repo_data)
        pipeline_time = (time.time() - start_pipeline) * 1000.0

        # Add performance metrics to the metadata
        total_time = fetch_time + pipeline_time

        # 3. Map V3 report into backward-compatible V2 structure for the UI
        # Get status from score
        score = report.scorecard.overall_score
        if score >= 9.0:
            status = "ELITE"
        elif score >= 7.5:
            status = "STRONG"
        elif score >= 6.0:
            status = "INTERVIEW"
        elif score >= 3.0:
            status = "POLISH"
        else:
            status = "REJECT"

        # Map recommendations to UI checklist format
        ui_checklist = []
        if report.narrative:
            for rec in report.narrative.recommendations:
                ui_checklist.append({
                    "title": rec.title,
                    "impact": rec.impact,
                    "hiring_impact": rec.description
                })
        else:
            # Fallback checklist if AI narrative failed
            for res in report.scorecard.rule_results:
                if not res.passed:
                    ui_checklist.append({
                        "title": res.rule_id,
                        "impact": "High" if "LICENSE" in res.rule_id or "TEST" in res.rule_id else "Medium",
                        "hiring_impact": res.failure_reason
                    })

        # Map rule results to UI audits format
        ui_audits = []
        rule_label_map = {
            "RULE_001_LICENSE_EXISTS": "License (MIT/GPL)",
            "RULE_002_README_SETUP": "Detailed Setup Guide",
            "RULE_003_README_DEMO": "Visual Demos",
            "RULE_004_CICD_WORKFLOWS": "Architecture Highlights",
            "RULE_005_TESTING_SUITE": "Technology Summary",
            "RULE_007_CONTRIBUTING_GUIDE": "Contribution Guidelines",
            "RULE_009_FRAMEWORK_MATURITY": "Project Description"
        }
        for res in report.scorecard.rule_results:
            label = rule_label_map.get(res.rule_id)
            if label:
                ui_audits.append({
                    "label": label,
                    "passed": res.passed
                })

        return {
            "logic_scratchpad": f"Base: 5.0 | Normal: {report.scorecard.overall_score}",
            "score": score,
            "status": status,
            "feedback": report.narrative.recruiter_verdict if report.narrative else "Audit completed.",
            "wow_insight": {
                "title": "Signal Detected",
                "description": report.narrative.summary if report.narrative else "Repository parsing completed successfully."
            },
            "checklist": ui_checklist,
            "readme_audits": ui_audits,
            "timings_ms": {
                "fetch": round(fetch_time, 2),
                "pipeline": round(pipeline_time, 2),
                "total": round(total_time, 2)
            }
        }
