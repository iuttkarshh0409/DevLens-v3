from typing import List, Type
from app.rie.base import BaseAnalyzer

class AnalyzerRegistry:
    def __init__(self):
        self._analyzers: List[BaseAnalyzer] = []

    def register(self, analyzer: BaseAnalyzer) -> None:
        if analyzer not in self._analyzers:
            self._analyzers.append(analyzer)
            # Keep sorted by priority (lowest first or highest first - let's sort by priority value)
            self._analyzers.sort(key=lambda a: a.priority)

    def get_analyzers(self) -> List[BaseAnalyzer]:
        return self._analyzers

# Create a default registry instance
registry = AnalyzerRegistry()
