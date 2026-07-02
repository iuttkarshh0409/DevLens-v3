from abc import ABC, abstractmethod
from app.models.analysis import EvidenceGraph, AnalyzerResult

class AnalyzerContext:
    def __init__(self, evidence_graph: EvidenceGraph):
        self.evidence_graph = evidence_graph

class BaseAnalyzer(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        pass

    @abstractmethod
    def analyze(self, context: AnalyzerContext) -> AnalyzerResult:
        pass
