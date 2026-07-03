import json
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import StreamingResponse, JSONResponse
from datetime import datetime, timedelta

# Local imports
from app.models.analytics import RepositoryHealthView
from app.services.analytics_service import (
    AnalyticsService,
    InMemoryAnalyticsStore,
    TrendEngine,
    ExportService
)

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

# Shared in-memory store instance
shared_store = InMemoryAnalyticsStore()
shared_analytics = AnalyticsService(shared_store)

# Redis mock cache simulation
_redis_mock_cache = {}

def get_installation_id() -> int:
    # Simulates OAuth/JWT token parsing middleware resolving installation context
    return 12345

@router.get("/overview")
async def get_overview(
    installation_id: int = Depends(get_installation_id),
    refresh_cache: bool = Query(False)
):
    cache_key = f"analytics:v1:{installation_id}"
    
    if not refresh_cache and cache_key in _redis_mock_cache:
        # Cache Hit
        return json.loads(_redis_mock_cache[cache_key])

    # Cache Miss / Warmup
    widgets = shared_analytics.get_dashboard_widgets(installation_id)
    _redis_mock_cache[cache_key] = json.dumps(widgets)
    return widgets

@router.get("/trends")
async def get_trends(
    interval: str = Query("weekly", regex="^(hourly|daily|weekly|monthly)$"),
    aggregation: str = Query("average", regex="^(average|sum|max|median|percentile|rolling_average)$"),
    installation_id: int = Depends(get_installation_id)
):
    records = shared_store.get_audit_records(installation_id=installation_id)
    time_series = TrendEngine.calculate_trends(records, interval, aggregation)
    return time_series

@router.get("/repositories")
async def get_repositories(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    installation_id: int = Depends(get_installation_id)
):
    healths = shared_store.get_health_records(installation_id)
    
    # Simple cursor/offset pagination
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
    records = shared_store.get_audit_records(installation_id=installation_id)
    
    # Filter by range range_str
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
    
    # CSV format streaming response
    csv_string = ExportService.generate_csv_export(filtered)
    
    return StreamingResponse(
        iter([csv_string]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=devlens_export_{installation_id}.csv"}
    )
