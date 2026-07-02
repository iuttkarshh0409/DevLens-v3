from typing import Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

# Local imports
from app.core.logging import logger
from app.models.request import AnalyzeRequest
from app.services.audit import AuditService
from app.webhooks.router import router as webhooks_router

app = FastAPI(title="DevLens Analysis API")

# Include Webhooks Router
app.include_router(webhooks_router)

# Initialize Audit Service
audit_service = AuditService()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://[::1]:5173",
        "http://localhost:3000",
        "https://dev-lens-lime.vercel.app",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Integrated Endpoints
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "DevLens Analysis Engine"}

@app.post("/analyze")
async def analyze_repository(request: AnalyzeRequest):
    logger.info(f"Analyzing: {request.repo_url}")
    analysis = await audit_service.run_audit_flow(request.repo_url)
    return analysis

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
        "message": "GitHub App installed successfully. DevLens V3 is now active on this account."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
