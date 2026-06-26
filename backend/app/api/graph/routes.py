from fastapi import APIRouter, Depends, Query

from app.api.auth.dependencies import require_role
from app.services.graph import build_graph_for_equipment, get_graph_stats, search_graph_nodes

router = APIRouter(dependencies=[Depends(require_role("viewer", "engineer", "admin"))])


@router.get("/search")
def search_graph(q: str = Query("", description="Search query for graph nodes")) -> list[dict]:
    return search_graph_nodes(q)


@router.get("/stats")
def graph_statistics() -> dict[str, object]:
    return get_graph_stats()


@router.get("/{equipment_id}")
def get_knowledge_graph(equipment_id: str) -> dict:
    return build_graph_for_equipment(equipment_id)
