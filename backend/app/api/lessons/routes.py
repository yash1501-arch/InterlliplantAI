from fastapi import APIRouter, Depends

from app.api.auth.dependencies import require_role
from app.models.schemas import LessonsRequest
from app.services.graph import log_activity
from app.services.lessons import extract_lessons, get_recurring_patterns, list_lessons

router = APIRouter(dependencies=[Depends(require_role("viewer", "engineer", "admin"))])


@router.post("")
def lessons_learned(payload: LessonsRequest) -> dict:
    log_activity("lessons_extracted", f"Equipment: {payload.equipment or 'all'}")
    return extract_lessons(payload.equipment, payload.query)


@router.get("")
def get_lessons() -> list[dict]:
    return list_lessons()


@router.get("/patterns")
def recurring_patterns() -> list[dict]:
    return get_recurring_patterns()
