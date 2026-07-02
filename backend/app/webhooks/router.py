import hmac
import hashlib
import json
from typing import Optional
from fastapi import APIRouter, Request, HTTPException, Header
from app.core.config import GITHUB_WEBHOOK_SECRET
from app.core.logging import logger
from app.models.webhook import PushEvent, PullRequestEvent, InstallationEvent, RepositoryEvent, CheckSuiteEvent
from app.rie.pipeline import AuditPipeline

router = APIRouter(prefix="/github", tags=["webhooks"])

def verify_signature(payload_body: bytes, signature_header: Optional[str]) -> None:
    """Verifies that the webhook payload is signed with our secret key."""
    if not GITHUB_WEBHOOK_SECRET:
        # If secret is not set in config, skip validation (mostly local testing/development)
        return

    if not signature_header:
        raise HTTPException(status_code=401, detail="Missing X-Hub-Signature-256 header.")

    sha_name, signature = signature_header.split("=")
    if sha_name != "sha256":
        raise HTTPException(status_code=501, detail="Unsupported signature algorithm.")

    mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), msg=payload_body, digestmod=hashlib.sha256)
    if not hmac.compare_digest(mac.hexdigest(), signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature.")

@router.post("/webhook")
async def receive_webhook(
    request: Request,
    x_github_event: str = Header(..., alias="X-GitHub-Event"),
    x_github_delivery: str = Header(..., alias="X-GitHub-Delivery"),
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256")
):
    body_bytes = await request.body()
    
    # 1. Verify Signature
    verify_signature(body_bytes, x_hub_signature_256)
    
    # 2. Parse Body Data
    try:
        data = json.loads(body_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload.")

    logger.info(f"Webhook Delivery ID: {x_github_delivery} | Event: {x_github_event}")

    # 3. Route Event Type
    pipeline = AuditPipeline()
    
    try:
        if x_github_event == "ping":
            return {"status": "success", "message": "Pong"}
            
        elif x_github_event == "push":
            event = PushEvent(**data)
            if event.repository.archived or event.repository.fork:
                logger.info(f"Skipped push event for {event.repository.full_name} (Archived/Forked)")
                return {"status": "skipped", "reason": "Archived or fork repository."}
            
            # Execute audit synchronously
            # Create a mock repo data block from event parameters
            repo_data = {
                "name": event.repository.name,
                "stars": 0,
                "last_updated": datetime_now_str(),
                "readme": "README placeholder",
                "files": ["package.json"]  # Minimal mock files structure
            }
            await pipeline.execute_audit(repo_data)
            return {"status": "success", "event": "push", "audited": event.repository.full_name}
            
        elif x_github_event == "pull_request":
            event = PullRequestEvent(**data)
            if event.repository.archived:
                return {"status": "skipped", "reason": "Archived repo"}
            return {"status": "success", "event": "pull_request", "number": event.number}

        elif x_github_event == "installation":
            event = InstallationEvent(**data)
            return {"status": "success", "event": "installation", "action": event.action}

        elif x_github_event == "repository":
            event = RepositoryEvent(**data)
            return {"status": "success", "event": "repository", "action": event.action}

        elif x_github_event == "check_suite":
            event = CheckSuiteEvent(**data)
            return {"status": "success", "event": "check_suite", "sha": event.check_suite.head_sha}

        else:
            logger.info(f"Ignored unknown GitHub webhook event: {x_github_event}")
            return {"status": "ignored", "event": x_github_event}

    except Exception as e:
        logger.error(f"Failed to process event {x_github_event}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal webhook processing error.")

def datetime_now_str() -> str:
    from datetime import datetime
    return datetime.utcnow().isoformat() + "Z"
