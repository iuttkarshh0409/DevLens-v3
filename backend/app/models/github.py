from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class RepositorySnapshot(BaseModel):
    name: str
    stars: int = 0
    last_updated: str = ""
    readme: str = ""
    files: List[str] = Field(default_factory=list)
    devlens_config: Optional[str] = None
    raw_files_content: Dict[str, str] = Field(default_factory=dict)

