from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class WebhookRepository(BaseModel):
    id: int
    name: str
    full_name: str
    private: bool
    fork: bool
    archived: bool = False

class WebhookInstallation(BaseModel):
    id: int
    account: Optional[Dict[str, Any]] = None

class PushEvent(BaseModel):
    ref: str
    before: str
    after: str
    repository: WebhookRepository
    installation: Optional[WebhookInstallation] = None

class PullRequestPayload(BaseModel):
    number: int
    title: str
    state: str
    head: Dict[str, Any]
    base: Dict[str, Any]

class PullRequestEvent(BaseModel):
    action: str
    number: int
    pull_request: PullRequestPayload
    repository: WebhookRepository
    installation: Optional[WebhookInstallation] = None

class InstallationEvent(BaseModel):
    action: str
    installation: WebhookInstallation
    repositories: Optional[List[Dict[str, Any]]] = None

class RepositoryEvent(BaseModel):
    action: str
    repository: WebhookRepository
    installation: Optional[WebhookInstallation] = None

class CheckSuitePayload(BaseModel):
    id: int
    status: str
    conclusion: Optional[str] = None
    head_sha: str

class CheckSuiteEvent(BaseModel):
    action: str
    check_suite: CheckSuitePayload
    repository: WebhookRepository
    installation: Optional[WebhookInstallation] = None
