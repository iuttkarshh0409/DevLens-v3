from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class AuditJob(BaseModel):
    job_id: str
    repo_data: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    retries: int = 0
    max_retries: int = 3
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class JobResult(BaseModel):
    job_id: str
    status: JobStatus
    result_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
