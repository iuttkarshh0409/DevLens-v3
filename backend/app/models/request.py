from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    repo_url: str = Field(..., example="https://github.com/user/repo")
