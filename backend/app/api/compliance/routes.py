from fastapi import APIRouter, Depends

from app.api.auth.dependencies import require_role
from app.models.schemas import ComplianceCheckRequest
from app.services.compliance import check_compliance, get_available_standards, get_compliance_history
from app.services.graph import log_activity

router = APIRouter(dependencies=[Depends(require_role("viewer", "engineer", "admin"))])


@router.post("/check")
def compliance_check(payload: ComplianceCheckRequest) -> dict:
    log_activity("compliance_check", f"Document: {payload.document_id or 'all'}")
    return check_compliance(payload.document_id, payload.query)


@router.get("/standards")
def list_standards() -> list[dict]:
    return get_available_standards()


@router.get("/history")
def compliance_history() -> list[dict]:
    return get_compliance_history()
