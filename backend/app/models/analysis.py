from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class DetectedFramework(BaseModel):
    name: str
    confidence: float

class DetectedDependency(BaseModel):
    name: str
    version: Optional[str] = None
    ecosystem: str

class DetectedWorkflow(BaseModel):
    name: str
    path: str

class DetectedTestFramework(BaseModel):
    name: str
    confidence: float

class DetectedArchitecture(BaseModel):
    pattern: str
    evidence: List[str]

class RepositoryMetadata(BaseModel):
    name: str
    stars: int
    last_updated: str
    primary_language: Optional[str] = None

class EvidenceGraph(BaseModel):
    metadata: RepositoryMetadata
    files: List[str]
    readme: str
    raw_response: Optional[Dict[str, Any]] = None

class AnalyzerResult(BaseModel):
    analyzer_name: str
    passed: bool
    evidence: Dict[str, Any]

class RepositoryAnalysis(BaseModel):
    repo_name: str
    scoring_schema_version: str = "3.0.0"
    evidence_graph: EvidenceGraph
    results: Dict[str, AnalyzerResult]
    warnings: List[str] = Field(default_factory=list)
