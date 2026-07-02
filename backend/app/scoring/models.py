from pydantic import BaseModel
from typing import Dict, List, Optional
from datetime import datetime

class RuleResult(BaseModel):
    rule_id: str
    description: str
    passed: bool
    points_awarded: float
    max_points: float
    failure_reason: Optional[str] = None

class CategoryScore(BaseModel):
    category_name: str
    raw_score: float
    weighted_score: float
    max_contribution: float

class ScoreReport(BaseModel):
    overall_score: float
    category_scores: Dict[str, CategoryScore]
    rule_results: List[RuleResult]
    scoring_version: str
    timestamp: datetime
