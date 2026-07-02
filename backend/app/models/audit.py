from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.analysis import RepositoryAnalysis
from app.scoring.models import ScoreReport

class Recommendation(BaseModel):
    title: str
    description: str
    impact: str = Field(..., description="High, Medium, or Low")

class PriorityItem(BaseModel):
    label: str
    passed: bool
    hiring_impact: str

class NarrativeSection(BaseModel):
    summary: str
    recruiter_verdict: str
    maturity_estimate: str
    recommendations: List[Recommendation]
    priority_checklist: List[PriorityItem]

class AuditMetadata(BaseModel):
    repo_name: str
    commit_sha: Optional[str] = None
    scoring_version: str
    timestamp: datetime

class ExecutionSummary(BaseModel):
    rie_completed: bool
    scoring_completed: bool
    narrative_completed: bool

class AuditReport(BaseModel):
    metadata: AuditMetadata
    analysis: RepositoryAnalysis
    scorecard: ScoreReport
    narrative: Optional[NarrativeSection] = None
    execution: ExecutionSummary
