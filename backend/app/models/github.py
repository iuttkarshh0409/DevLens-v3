from pydantic import BaseModel, Field
from typing import List, Optional

class RepositorySnapshot(BaseModel):
    name: str
    stars: int = 0
    last_updated: str = ""
    readme: str = ""
    files: List[str] = Field(default_factory=list)
