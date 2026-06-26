import logging
from typing import Any

from app.db.database import get_connection
from app.services.entities import extract_entities
from app.services.neo4j_service import (
    build_graph_from_entities,
    get_graph_for_equipment as neo4j_get_graph,
    get_graph_stats as neo4j_get_stats,
    init_graph,
    is_connected,
    save_document_node,
    search_graph_nodes as neo4j_search,
)
from app.services.relationships import extract_relationships

logger = logging.getLogger(__name__)


def _load_graph_data() -> tuple[list[dict], list[dict], list[str]]:
    if is_connected():
        init_graph()
    with get_connection() as conn:
        rows = conn.execute("SELECT text FROM document_texts").fetchall()
    texts = [row["text"] for row in rows if row["text"]]
    combined = " ".join(texts) if texts else ""

    entities = extract_entities(combined)
    relationships = extract_relationships(entities, combined)

    entity_names = [e["entity"] for e in entities]

    if is_connected():
        try:
            build_graph_from_entities(entities, relationships)
        except Exception as e:
            logger.warning("Neo4j graph build failed: %s", e)

    nodes = []
    for i, ent in enumerate(entities):
        node_type = ent["type"]
        group = "equipment" if node_type == "EQUIPMENT" else node_type.lower()
        nodes.append({
            "id": f"ent-{i}",
            "label": ent["entity"],
            "type": node_type,
            "group": group,
            "properties": {
                "confidence": ent["confidence"],
                "context": ent["context"],
            },
        })

    edges = []
    edge_types_seen: set[tuple[str, str]] = set()
    for i, rel in enumerate(relationships):
        source_idx = entity_names.index(rel["source"]) if rel["source"] in entity_names else -1
        target_idx = entity_names.index(rel["target"]) if rel["target"] in entity_names else -1
        if source_idx >= 0 and target_idx >= 0:
            edge_key = (f"ent-{source_idx}", f"ent-{target_idx}")
            if edge_key not in edge_types_seen:
                edge_types_seen.add(edge_key)
                edges.append({
                    "id": i,
                    "source": f"ent-{source_idx}",
                    "target": f"ent-{target_idx}",
                    "type": rel["type"],
                    "properties": {"confidence": rel.get("confidence", 1.0)},
                })

    return nodes, edges, entity_names


def build_graph_for_equipment(eid: str, entities: list[dict] | None = None, relationships: list[dict] | None = None) -> dict:
    if is_connected():
        try:
            result = neo4j_get_graph(eid)
            if result.get("nodes"):
                return result
        except Exception as e:
            logger.warning("Neo4j graph query failed, using fallback: %s", e)

    nodes, edges, _ = _load_graph_data()

    eid_lower = eid.lower().replace("-", "").replace("_", "").replace(" ", "")

    # Match nodes by label containing the search term
    matched_node_ids: set[str] = set()
    for n in nodes:
        label_normalized = n["label"].lower().replace("-", "").replace("_", "").replace(" ", "")
        if eid_lower in label_normalized or label_normalized in eid_lower:
            matched_node_ids.add(n["id"])

    # If no direct match, do broader substring search
    if not matched_node_ids:
        for n in nodes:
            if eid.lower() in n["label"].lower() or n["label"].lower() in eid.lower():
                matched_node_ids.add(n["id"])

    # Expand to neighbors (1-hop)
    neighbor_ids: set[str] = set(matched_node_ids)
    for e in edges:
        if e["source"] in matched_node_ids:
            neighbor_ids.add(e["target"])
        if e["target"] in matched_node_ids:
            neighbor_ids.add(e["source"])

    # If still no match, return all nodes (max 25)
    if not neighbor_ids:
        neighbor_ids = {n["id"] for n in nodes[:25]}

    equipment_nodes = [n for n in nodes if n["id"] in neighbor_ids]
    equipment_edges = [
        e for e in edges
        if e["source"] in neighbor_ids and e["target"] in neighbor_ids
    ]

    return {
        "nodes": equipment_nodes,
        "edges": equipment_edges,
    }


def search_graph_nodes(query: str) -> list[dict]:
    if is_connected():
        try:
            return neo4j_search(query)
        except Exception as e:
            logger.warning("Neo4j search failed: %s", e)

    nodes, _, _ = _load_graph_data()
    return [
        {"id": n["id"], "name": n["label"], "types": [n["type"]]}
        for n in nodes
        if query.lower() in n["label"].lower()
    ][:20]


def get_graph_stats() -> dict:
    if is_connected():
        try:
            return neo4j_get_stats()
        except Exception as e:
            logger.warning("Neo4j stats failed: %s", e)

    nodes, edges, _ = _load_graph_data()
    type_counts: dict[str, int] = {}
    for n in nodes:
        t = n["type"]
        type_counts[t] = type_counts.get(t, 0) + 1

    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "node_types": type_counts,
    }


def get_dashboard_metrics() -> dict:
    with get_connection() as conn:
        docs = conn.execute("SELECT COUNT(*) as c FROM documents").fetchone()
        sessions = conn.execute("SELECT COUNT(*) as c FROM chat_sessions").fetchone()
        messages = conn.execute("SELECT COUNT(*) as c FROM chat_messages").fetchone()
        recent = conn.execute(
            "SELECT id, filename as name, size, status, created_at as uploaded_at FROM documents ORDER BY created_at DESC LIMIT 5"
        ).fetchall()

    graph_stats = get_graph_stats()
    equipment_count = graph_stats.get("node_types", {}).get("EQUIPMENT", 0)
    if equipment_count == 0:
        equipment_count = graph_stats.get("node_count", 0)

    return {
        "documents": docs["c"] if docs else 0,
        "sessions": sessions["c"] if sessions else 0,
        "messages": messages["c"] if messages else 0,
        "equipment": equipment_count,
        "recent_documents": [dict(r) for r in recent] if recent else [],
    }


def get_dashboard_trends(days: int = 30) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT DATE(created_at) as day, COUNT(*) as count
            FROM documents
            WHERE created_at >= DATE('now', ?)
            GROUP BY day
            ORDER BY day
            """,
            (f"-{days} days",),
        ).fetchall()
    return [{"date": r["day"], "documents": r["count"]} for r in rows]


def get_activity_log(limit: int = 20) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id as doc_id, filename, status, created_at FROM documents ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [
        {
            "type": "document_upload",
            "description": f"Uploaded {r['filename']}",
            "timestamp": r["created_at"],
        }
        for r in rows
    ]


def log_activity(activity_type: str, description: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO activity_log (action, detail) VALUES (?, ?)",
            (activity_type, description),
        )
        conn.commit()
