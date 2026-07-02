from typing import Dict, Any, Union
from app.models.analysis import EvidenceGraph, RepositoryMetadata, RepositoryAnalysis
from app.models.github import RepositorySnapshot
from app.rie.builder import EvidenceGraphBuilder
from app.rie.base import AnalyzerContext
from app.rie.registry import registry

# Ensure registry is initialized
import app.rie

class AnalysisOrchestrator:
    @staticmethod
    def run_analysis(repo_data: Union[Dict[str, Any], RepositorySnapshot]) -> RepositoryAnalysis:
        if isinstance(repo_data, dict):
            snapshot = RepositorySnapshot(**repo_data)
        else:
            snapshot = repo_data

        # 1. Build construction graph via Builder DTO
        evidence_graph = EvidenceGraphBuilder.build_evidence_graph(snapshot)

        # 3. Create AnalyzerContext
        context = AnalyzerContext(evidence_graph=evidence_graph)

        # 4. Execute registered analyzers
        results = {}
        for analyzer in registry.get_analyzers():
            result = analyzer.analyze(context)
            results[analyzer.name] = result

        # 5. Return compiled RepositoryAnalysis
        return RepositoryAnalysis(
            repo_name=evidence_graph.metadata.name,
            evidence_graph=evidence_graph,
            results=results
        )
