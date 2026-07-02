from app.models.github import RepositorySnapshot
from app.models.analysis import EvidenceGraph, RepositoryMetadata

class EvidenceGraphBuilder:
    @staticmethod
    def build_evidence_graph(snapshot: RepositorySnapshot) -> EvidenceGraph:
        metadata = RepositoryMetadata(
            name=snapshot.name,
            stars=snapshot.stars,
            last_updated=snapshot.last_updated
        )
        return EvidenceGraph(
            metadata=metadata,
            files=snapshot.files,
            readme=snapshot.readme
        )
