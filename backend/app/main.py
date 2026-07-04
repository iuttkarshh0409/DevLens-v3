from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# Local imports
from app.core.logging import logger
from app.models.request import AnalyzeRequest
from app.services.audit import AuditService
from app.webhooks.router import router as webhooks_router
from app.api.badges import router as badges_router
from app.api.analytics import router as analytics_router

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup lifecycle hooks
    logger.info("Initializing DevLens Analysis API...")
    yield
    # Shutdown lifecycle hooks
    logger.info("DevLens Shutting down services...")
    
    # 1. Dispose SQLAlchemy connection pools
    from app.database.connection import engine
    await engine.dispose()
    logger.info("SQLAlchemy connection engine pool disposed.")
    
    # 2. Close Redis client connection
    from app.api.analytics import redis_client
    if redis_client:
        try:
            redis_client.close()
            logger.info("Redis cache client closed.")
        except Exception:
            pass

app = FastAPI(title="DevLens Analysis API", lifespan=lifespan)

# Include Routers
app.include_router(webhooks_router)
app.include_router(badges_router)
app.include_router(analytics_router)

# Initialize Audit Service
audit_service = AuditService()

from app.core.config import ALLOWED_ORIGINS, DEVLENS_ENV

# CORS Middleware
origins = ALLOWED_ORIGINS if DEVLENS_ENV.lower() == "production" else [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://[::1]:5173",
    "http://localhost:3000",
    "https://dev-lens-lime.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.core.context import RequestContext

@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Initialize RequestContext for tracking
    ctx = RequestContext()
    request.state.request_context = ctx
    logger.info(f"Incoming request {ctx.request_id}: {request.method} {request.url}")
    
    response = await call_next(request)
    logger.info(f"Response status {ctx.request_id}: {response.status_code}")
    return response

# Integrated Endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "DevLens Analysis Engine"}

from fastapi.responses import Response
from app.observability.metrics import metrics_registry

@app.get("/metrics")
async def get_metrics():
    content = metrics_registry.generate_prometheus_output()
    return Response(content=content, media_type="text/plain; version=0.0.4; charset=utf-8")

@app.post("/analyze")
async def analyze_repository(request: Request, analyze_req: AnalyzeRequest):
    ctx = getattr(request.state, "request_context", None) or RequestContext()
    logger.info(f"Analyzing repo URL {analyze_req.repo_url} with request {ctx.request_id}")
    analysis = await audit_service.run_audit_flow(analyze_req.repo_url, request_context=ctx)
    return analysis

from app.jobs import shared_queue

@app.get("/jobs/health")
async def jobs_health(job_id: Optional[str] = None):
    metrics = shared_queue.get_metrics()
    status_info = None
    if job_id:
        status_info = shared_queue.status(job_id)
        
    return {
        "status": "healthy",
        "redis_connected": shared_queue.active,
        "metrics": metrics,
        "queried_job_status": status_info
    }

@app.get("/app/install")
async def app_install():
    # Redirect directly to GitHub App installation flow
    app_url = "https://github.com/apps/devlens-v3/installations/new"
    return RedirectResponse(url=app_url)

@app.get("/app/callback")
async def app_callback(installation_id: Optional[int] = None, setup_action: Optional[str] = None):
    if not installation_id:
        raise HTTPException(status_code=400, detail="Missing installation_id parameter.")
    return {
        "status": "success",
        "installation_id": installation_id,
        "setup_action": setup_action,
        "onboarding": {
            "message": "GitHub App installed successfully. DevLens V3 is now active on your repositories.",
            "next_steps": [
                "1. Add a '.devlens.yml' file to the root of your repositories to customize audit rules.",
                "2. Open a Pull Request on any configured repository to trigger DevLens Checks and Reviews.",
                "3. Use our SVG badges in your README.md to display your repository score."
            ],
            "active_permissions": {
                "checks": "write",
                "pull_requests": "write",
                "statuses": "write",
                "metadata": "read"
            },
            "badge_url": f"http://localhost:8000/api/badge?label=devlens&value=active"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
