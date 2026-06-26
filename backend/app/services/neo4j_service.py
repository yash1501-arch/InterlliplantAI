import logging
from typing import Any

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

from app.config import settings

logger = logging.getLogger(__name__)

_driver = None


def _get_driver():
    global _driver
    if _driver is None:
        try:
            _driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
                max_connection_lifetime=3600,
            )
            _driver.verify_connectivity()
            logger.info("Connected to Neo4j at %s", settings.neo4j_uri)
        except Exception as e:
            logger.warning("Neo4j connection failed: %s — using fallback", e)
            _driver = None
    return _driver


def is_connected() -> bool:
    d = _get_driver()
    return d is not None


def _run_query(query: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    d = _get_driver()
    if d is None:
        return []
    try:
        with d.session() as session:
            result = session.run(query, params or {})
            return [dict(r) for r in result]
    except Exception as e:
        logger.warning("Neo4j query failed: %s", e)
        return []


def init_graph():
    if not is_connected():
        return
    _run_query("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Equipment) REQUIRE e.id IS UNIQUE")
    _run_query("CREATE CONSTRAINT IF NOT EXISTS FOR (f:Failure) REQUIRE f.id IS UNIQUE")
    _run_query("CREATE CONSTRAINT IF NOT EXISTS FOR (i:Incident) REQUIRE i.id IS UNIQUE")
    _run_query("CREATE CONSTRAINT IF NOT EXISTS FOR (r:Regulation) REQUIRE r.id IS UNIQUE")
    _run_query("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Personnel) REQUIRE p.id IS UNIQUE")
    _run_query("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.id IS UNIQUE")
    logger.info("Neo4j constraints initialized")


def _sanitize_id(text: str) -> str:
    return text.lower().replace(" ", "_").replace("-", "_").replace("/", "_")[:100]


def _get_node_label(entity_type: str) -> str:
    mapping = {
        "EQUIPMENT": "Equipment",
        "FAILURE": "Failure",
        "INCIDENT": "Incident",
        "REGULATION": "Regulation",
        "PERSONNEL": "Personnel",
    }
    return mapping.get(entity_type, "Entity")


def save_entity(entity_name: str, entity_type: str, document_id: str = "") -> str:
    label = _get_node_label(entity_type)
    node_id = _sanitize_id(entity_name)
    _run_query(
        f"""
        MERGE (n:{label} {{id: $node_id}})
        ON CREATE SET n.name = $name, n.first_seen = timestamp()
        ON MATCH SET n.last_seen = timestamp()
        WITH n
        WHERE $document_id <> ''
        OPTIONAL MATCH (d:Document {{id: $document_id}})
        FOREACH(_ IN CASE WHEN d IS NOT NULL THEN [1] ELSE [] END |
            MERGE (n)-[:DESCRIBED_BY]->(d)
        )
        """,
        {"node_id": node_id, "name": entity_name, "document_id": document_id},
    )
    return node_id


def save_relationship(
    source_name: str,
    target_name: str,
    rel_type: str,
    source_type: str = "",
    target_type: str = "",
    evidence: str = "",
):
    src_label = _get_node_label(source_type) if source_type else "Entity"
    tgt_label = _get_node_label(target_type) if target_type else "Entity"
    src_id = _sanitize_id(source_name)
    tgt_id = _sanitize_id(target_name)

    _run_query(
        f"""
        MATCH (s:{src_label} {{id: $src_id}})
        MATCH (t:{tgt_label} {{id: $tgt_id}})
        MERGE (s)-[r:{rel_type}]->(t)
        ON CREATE SET r.first_seen = timestamp(), r.evidence = $evidence
        ON MATCH SET r.last_seen = timestamp()
        """,
        {"src_id": src_id, "tgt_id": tgt_id, "evidence": evidence},
    )


def save_document_node(document_id: str, filename: str):
    _run_query(
        """
        MERGE (d:Document {id: $id})
        ON CREATE SET d.name = $name, d.created_at = timestamp()
        """,
        {"id": document_id, "name": filename},
    )


def get_graph_for_equipment(equipment_id: str) -> dict:
    if not is_connected():
        return {"nodes": [], "edges": []}

    nodes_raw = _run_query(
        """
        MATCH (e:Equipment {id: $id})-[r]-(connected)
        RETURN e, r, connected
        LIMIT 100
        """,
        {"id": equipment_id},
    )
    if not nodes_raw:
        n = _run_query(
            "MATCH (e:Equipment {id: $id}) RETURN e",
            {"id": equipment_id},
        )
        if n:
            return {
                "nodes": [{"id": equipment_id, "label": equipment_id, "type": "Equipment"}],
                "edges": [],
            }

    seen_nodes: dict[str, dict] = {}
    edges: list[dict] = []

    for row in nodes_raw:
        for key in ("e", "connected"):
            node = row.get(key)
            if node and isinstance(node, dict):
                nid = node.get("id", "")
                if nid and nid not in seen_nodes:
                    labels = list(node.get("labels", ["Entity"]))
                    seen_nodes[nid] = {
                        "id": nid,
                        "label": node.get("name", nid),
                        "type": labels[0] if labels else "Entity",
                    }

        rel = row.get("r")
        if rel and isinstance(rel, dict):
            edges.append({
                "source": rel.get("start_node", {}).get("id", "") if isinstance(rel.get("start_node"), dict) else "",
                "target": rel.get("end_node", {}).get("id", "") if isinstance(rel.get("end_node"), dict) else "",
                "type": list(rel.get("type", ["CONNECTED_TO"])) if isinstance(rel.get("type"), list) else rel.get("type", "CONNECTED_TO"),
            })

    return {
        "nodes": list(seen_nodes.values()),
        "edges": edges,
    }


def search_graph_nodes(query: str) -> list[dict]:
    if not is_connected():
        return []

    results = _run_query(
        """
        MATCH (n)
        WHERE n.name CONTAINS $query OR n.id CONTAINS $query
        RETURN n.id AS id, n.name AS name, labels(n) AS types
        LIMIT 20
        """,
        {"query": query},
    )
    return [
        {
            "id": r["id"],
            "name": r.get("name", r["id"]),
            "types": r.get("types", ["Entity"]),
        }
        for r in results
    ]


def get_graph_stats() -> dict:
    if not is_connected():
        return {"node_count": 0, "edge_count": 0, "node_types": {}}

    node_count = _run_query("MATCH (n) RETURN count(n) AS count")
    edge_count = _run_query("MATCH ()-[r]->() RETURN count(r) AS count")
    type_counts = _run_query(
        "MATCH (n) RETURN labels(n) AS type, count(n) AS count LIMIT 20"
    )

    return {
        "node_count": node_count[0]["count"] if node_count else 0,
        "edge_count": edge_count[0]["count"] if edge_count else 0,
        "node_types": {
            r["type"][0] if isinstance(r["type"], list) else str(r["type"]): r["count"]
            for r in type_counts
        }
        if type_counts
        else {},
    }


def build_graph_from_entities(
    entities: list[dict],
    relationships: list[dict],
    document_id: str = "",
):
    if not is_connected():
        return

    for ent in entities:
        save_entity(ent["entity"], ent["type"], document_id)

    for rel in relationships:
        save_relationship(
            rel["source"],
            rel["target"],
            rel["type"],
            source_type=rel.get("source_type", ""),
            target_type=rel.get("target_type", ""),
            evidence=rel.get("evidence", ""),
        )


def close():
    global _driver
    if _driver:
        _driver.close()
        _driver = None
