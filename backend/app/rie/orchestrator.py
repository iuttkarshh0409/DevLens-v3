from typing import Dict, Any, Union, Optional
from app.models.analysis import EvidenceGraph, RepositoryMetadata, RepositoryAnalysis, AnalyzerResult
from app.models.github import RepositorySnapshot
from app.rie.builder import EvidenceGraphBuilder
from app.rie.base import AnalyzerContext
from app.rie.registry import registry
from app.core.context import RequestContext
from app.core.logging import logger

# Ensure registry is initialized
import app.rie

class AnalysisOrchestrator:
    @staticmethod
    def run_analysis(
        repo_data: Union[Dict[str, Any], RepositorySnapshot],
        request_context: Optional[RequestContext] = None
    ) -> RepositoryAnalysis:
        ctx = request_context or RequestContext()
        logger.info(f"Running AnalysisOrchestrator for request: {ctx.request_id}")

        if isinstance(repo_data, dict):
            snapshot = RepositorySnapshot(**repo_data)
        else:
            snapshot = repo_data

        # 1. Build construction graph via Builder DTO
        evidence_graph = EvidenceGraphBuilder.build_evidence_graph(snapshot)

        # 3. Create AnalyzerContext
        context = AnalyzerContext(evidence_graph=evidence_graph)

        # 4. Execute registered analyzers with sandboxed isolation
        results = {}
        warnings = []
        for analyzer in registry.get_analyzers():
            start_time = time_now_ms()
            try:
                result = analyzer.analyze(context)
                results[analyzer.name] = result
                duration = time_now_ms() - start_time
                logger.info(f"Analyzer {analyzer.name} finished in {duration:.2f}ms")
            except Exception as e:
                warn_msg = f"Analyzer {analyzer.name} failed: {str(e)}"
                logger.error(warn_msg)
                warnings.append(warn_msg)
                results[analyzer.name] = AnalyzerResult(
                    analyzer_name=analyzer.name,
                    passed=False,
                    evidence={}
                )

        # 5. Return compiled RepositoryAnalysis
        return RepositoryAnalysis(
            repo_name=evidence_graph.metadata.name,
            evidence_graph=evidence_graph,
            results=results,
            warnings=warnings
        )

def time_now_ms() -> float:
    import time
    return time.time() * 1000.0
