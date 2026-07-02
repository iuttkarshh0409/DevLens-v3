from typing import Dict, Any
from app.models.analysis import EvidenceGraph, RepositoryMetadata, RepositoryAnalysis
from app.rie.base import AnalyzerContext
from app.rie.registry import registry

# Ensure registry is initialized
import app.rie

class AnalysisOrchestrator:
    @staticmethod
    def run_analysis(repo_data: Dict[str, Any]) -> RepositoryAnalysis:
        # 1. Build RepositoryMetadata
        metadata = RepositoryMetadata(
            name=repo_data.get("name", "unknown"),
            stars=repo_data.get("stars", 0),
            last_updated=repo_data.get("last_updated", "")
        )

        # 2. Construct EvidenceGraph
        evidence_graph = EvidenceGraph(
            metadata=metadata,
            files=repo_data.get("files", []),
            readme=repo_data.get("readme", "")
        )

        # 3. Create AnalyzerContext
        context = AnalyzerContext(evidence_graph=evidence_graph)

        # 4. Execute registered analyzers
        results = {}
        for analyzer in registry.get_analyzers():
            result = analyzer.analyze(context)
            results[analyzer.name] = result

        # 5. Return compiled RepositoryAnalysis
        return RepositoryAnalysis(
            repo_name=metadata.name,
            evidence_graph=evidence_graph,
            results=results
        )
