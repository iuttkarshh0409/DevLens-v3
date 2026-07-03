from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class TrendPoint(BaseModel):
    timestamp: datetime
    value: float
    pass_count: int
    fail_count: int

class EvidenceSummary(BaseModel):
    passed_rules: List[str] = Field(default_factory=list)
    failed_rules: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    licenses: List[str] = Field(default_factory=list)
    ci: List[str] = Field(default_factory=list)
    testing: List[str] = Field(default_factory=list)
    deployment: List[str] = Field(default_factory=list)
    architecture: str = "Standard"
    security_findings: int = 0
    documentation_findings: int = 0
    testing_findings: int = 0

class AuditHistoryRecord(BaseModel):
    audit_id: str
    repository_id: str
    repo_name: str
    installation_id: int
    score: float
    status: str
    scoring_version: str
    devlens_version: str
    commit_sha: str
    branch: str
    audit_duration_ms: int
    trigger_type: str  # "manual", "push", "pull_request", "nightly"
    warnings_count: int
    timestamp: datetime
    evidence: EvidenceSummary

class RepositoryHealthRecord(BaseModel):
    repository_id: str
    repo_name: str
    health_score: float
    last_audit: datetime
    trend: str  # "up", "down", "stable"
    risk_level: str  # "low", "medium", "high"
    critical_findings: int
    documentation_score: float
    security_score: float
    testing_score: float

class RepositoryHealthView(BaseModel):
    repository_id: str
    repo_name: str
    health_score: float
    last_audit: datetime
    trend: str
    risk_level: str
    critical_findings: int
    documentation_score: float
    security_score: float
    testing_score: float

class TimeSeries(BaseModel):
    interval: str  # "hourly", "daily", "weekly", "monthly"
    aggregation: str  # "average", "sum", "max", "median", "percentile", "rolling_average"
    points: List[TrendPoint] = Field(default_factory=list)
