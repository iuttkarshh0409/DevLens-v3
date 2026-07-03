import time
import uuid
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class RequestContext(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    audit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    installation_id: Optional[int] = None
    user_id: Optional[str] = None
    github_delivery_id: Optional[str] = None
    start_time: float = Field(default_factory=time.time)
    trace_metadata: Dict[str, Any] = Field(default_factory=dict)
