from datetime import datetime
from typing import Dict, Any, Optional
from app.rie.orchestrator import AnalysisOrchestrator
from app.scoring.engine import ScoringEngine
from app.ai.narrative import NarrativeEngine, AuditContext
from app.ai.provider import BaseAIProvider
from app.models.audit import AuditReport, AuditMetadata, ExecutionSummary

class AuditPipeline:
    def __init__(self, ai_provider: Optional[BaseAIProvider] = None):
        self.ai_provider = ai_provider
        self.narrative_engine = NarrativeEngine(ai_provider) if ai_provider else None

    async def execute_audit(self, repo_data: Dict[str, Any], role: str = "recruiter") -> AuditReport:
        # 1. Execute RIE Orchestration
        analysis = AnalysisOrchestrator.run_analysis(repo_data)
        rie_completed = True

        # 2. Execute Scoring Engine
        scorecard = ScoringEngine.calculate_score(analysis)
        scoring_completed = True

        # 3. Compile context and query narrative engine if provider is configured
        narrative_section = None
        narrative_completed = False
        if self.narrative_engine:
            context = AuditContext(analysis=analysis, scorecard=scorecard)
            try:
                narrative_section = await self.narrative_engine.generate_report_section(context, role=role)
                narrative_completed = True
            except Exception:
                # Graceful recovery if LLM provider fails
                narrative_completed = False

        # 4. Formulate Execution Summary
        execution = ExecutionSummary(
            rie_completed=rie_completed,
            scoring_completed=scoring_completed,
            narrative_completed=narrative_completed
        )

        # 5. Formulate Metadata
        metadata = AuditMetadata(
            repo_name=analysis.repo_name,
            scoring_version=scorecard.scoring_version,
            timestamp=datetime.utcnow()
        )

        return AuditReport(
            metadata=metadata,
            analysis=analysis,
            scorecard=scorecard,
            narrative=narrative_section,
            execution=execution
        )
