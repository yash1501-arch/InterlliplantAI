from fastapi import APIRouter, Depends, Query

from app.api.auth.dependencies import require_role
from app.services.graph import get_activity_log, get_dashboard_metrics, get_dashboard_trends

router = APIRouter(dependencies=[Depends(require_role("viewer", "engineer", "admin"))])


@router.get("/metrics")
def dashboard_metrics() -> dict:
    return get_dashboard_metrics()


@router.get("/trends")
def dashboard_trends(days: int = Query(30, description="Number of days of trend data")) -> list[dict]:
    return get_dashboard_trends(days)


@router.get("/activity")
def dashboard_activity(limit: int = Query(20, description="Number of activity entries")) -> list[dict]:
    return get_activity_log(limit)
