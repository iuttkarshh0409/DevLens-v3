from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ExpectedBenchmark(BaseModel):
    repo_name: str
    expected_framework: str
    expected_architecture: str
    min_score: float
    max_score: float
    expected_findings: List[str]
    difficulty_level: str
    tags: List[str]

class BenchmarkResult(BaseModel):
    repo_name: str
    passed: bool
    actual_score: float
    score_difference: float
    mismatched_rules: List[str]
    mismatched_findings: List[str]
    execution_time_ms: float

class BenchmarkReport(BaseModel):
    overall_pass_rate: float
    total_benchmarks: int
    passed_count: int
    failed_count: int
    results: List[BenchmarkResult]
    timestamp: datetime
