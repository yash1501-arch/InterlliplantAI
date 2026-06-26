from fastapi import APIRouter, Depends

from app.api.auth.dependencies import require_role
from app.db.database import get_connection
from app.models.schemas import SearchRequest
from app.services.graph import log_activity
from app.services.retrieval import build_demo_search_result, search_with_pagination

router = APIRouter(dependencies=[Depends(require_role("viewer", "engineer", "admin"))])


@router.post("")
def search_documents(payload: SearchRequest) -> dict:
    filters = payload.filters.model_dump() if payload.filters else None
    log_activity("search", f"Query: {payload.query[:50]}")
    return search_with_pagination(
        query=payload.query,
        page=payload.page,
        page_size=payload.page_size,
        filters=filters,
    )


@router.get("/recent")
def recent_searches() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, query, page, page_size, result_count, created_at FROM recent_searches ORDER BY created_at DESC LIMIT 20"
        ).fetchall()
    return [
        {
            "id": row["id"],
            "query": row["query"],
            "page": row["page"],
            "page_size": row["page_size"],
            "result_count": row["result_count"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]
