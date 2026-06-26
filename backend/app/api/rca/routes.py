from fastapi import APIRouter, Depends, HTTPException

from app.api.auth.dependencies import require_role
from app.models.schemas import RCARequest
from app.services.graph import log_activity
from app.services.rca import get_rca_detail, get_rca_history, perform_rca_analysis

router = APIRouter(dependencies=[Depends(require_role("viewer", "engineer", "admin"))])


@router.post("")
def rca_analysis(payload: RCARequest) -> dict:
    log_activity("rca_analysis", f"Equipment: {payload.equipment}")
    return perform_rca_analysis(payload.equipment)


@router.get("/history")
def rca_history() -> list[dict]:
    return get_rca_history()


@router.get("/{rca_id}")
def rca_detail(rca_id: str) -> dict[str, object]:
    result = get_rca_detail(rca_id)
    if not result:
        raise HTTPException(status_code=404, detail="RCA result not found")
    return result
