import json
import redis
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from datetime import datetime, timedelta

# Local imports
from app.models.analytics import RepositoryHealthView
from app.core.config import DEVLENS_ENV, DATABASE_URL, REDIS_URL, ANALYTICS_CACHE_TTL
from app.services.analytics_service import (
    AnalyticsService,
    InMemoryAnalyticsStore,
    TrendEngine,
    ExportService
)
from app.storage.sql_analytics_store import SQLAnalyticsStore
from app.database.connection import async_session

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

# Environment-based store selection
if DEVLENS_ENV.lower() == "production":
    shared_store = SQLAnalyticsStore(async_session)
else:
    shared_store = InMemoryAnalyticsStore()

shared_analytics = AnalyticsService(shared_store)

# Resilient Redis Cache Connection
redis_client = None
try:
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_timeout=2.0)
except Exception:
    pass

def invalidate_dashboard_cache(installation_id: int) -> None:
    """Invalidates the versioned Redis cache key for the organization."""
    if redis_client:
        try:
            redis_client.delete(f"analytics:v1:{installation_id}")
        except Exception:
            pass

# Attach cache invalidation callback to self-heal dashboard states
shared_analytics.on_completion_callback = invalidate_dashboard_cache

def get_installation_id() -> int:
    return 12345

@router.get("/overview")
async def get_overview(
    installation_id: int = Depends(get_installation_id),
    refresh_cache: bool = Query(False)
):
    cache_key = f"analytics:v1:{installation_id}"
    
    if not refresh_cache and redis_client:
        try:
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass

    # Cache Miss / Warmup
    widgets = await shared_analytics.get_dashboard_widgets(installation_id)
    
    if redis_client:
        try:
            redis_client.setex(cache_key, ANALYTICS_CACHE_TTL, json.dumps(widgets))
        except Exception:
            pass
            
    return widgets

@router.get("/trends")
async def get_trends(
    interval: str = Query("weekly", regex="^(hourly|daily|weekly|monthly)$"),
    aggregation: str = Query("average", regex="^(average|sum|max|median|percentile|rolling_average)$"),
    installation_id: int = Depends(get_installation_id)
):
    records = await shared_store.get_audit_records(installation_id=installation_id)
    time_series = TrendEngine.calculate_trends(records, interval, aggregation)
    return time_series

@router.get("/repositories")
async def get_repositories(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    installation_id: int = Depends(get_installation_id)
):
    healths = await shared_store.get_health_records(installation_id)
    
    # Cursor/Offset pagination
    start = (page - 1) * limit
    end = start + limit
    paginated = healths[start:end]
    
    return {
        "page": page,
        "limit": limit,
        "total_count": len(healths),
        "data": [
            RepositoryHealthView(
                repository_id=h.repository_id,
                repo_name=h.repo_name,
                health_score=h.health_score,
                last_audit=h.last_audit,
                trend=h.trend,
                risk_level=h.risk_level,
                critical_findings=h.critical_findings,
                documentation_score=h.documentation_score,
                security_score=h.security_score,
                testing_score=h.testing_score
            )
            for h in paginated
        ]
    }

@router.get("/export")
async def export_data(
    format: str = Query("csv", regex="^(csv|json)$"),
    installation_id: int = Depends(get_installation_id),
    range_str: str = Query("90d")
):
    records = await shared_store.get_audit_records(installation_id=installation_id)
    
    days = 90
    if range_str.endswith("d"):
        try:
            days = int(range_str[:-1])
        except ValueError:
            pass
            
    cutoff = datetime.utcnow() - timedelta(days=days)
    filtered = [r for r in records if r.timestamp >= cutoff]

    if format == "json":
        json_output = ExportService.generate_json_export(filtered, installation_id, range_str)
        return JSONResponse(content=json_output)
    
    csv_string = ExportService.generate_csv_export(filtered)
    
    return StreamingResponse(
        iter([csv_string]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=devlens_export_{installation_id}.csv"}
    )
