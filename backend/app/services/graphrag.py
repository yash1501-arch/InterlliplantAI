import re

from app.db.database import get_connection
from app.services.entities import extract_entities
from app.services.neo4j_service import is_connected, _run_query as neo4j_query
from app.services.relationships import extract_relationships


def build_context_summary(message: str) -> dict:
    with get_connection() as conn:
        rows = conn.execute("SELECT text FROM document_texts").fetchall()

    texts = [row["text"] for row in rows if row["text"]]

    all_entities = []
    for text in texts:
        all_entities.extend(extract_entities(text))

    seen = set()
    unique_entities = []
    for ent in all_entities:
        name = ent["entity"].lower()
        if name not in seen:
            seen.add(name)
            unique_entities.append(ent)

    combined = " ".join(texts) if texts else message

    relationships = extract_relationships(unique_entities, combined)

    neo4j_context = {}
    if is_connected():
        try:
            msg_entities = extract_entities(message)
            for e in msg_entities[:3]:
                node_id = e["entity"].lower().replace(" ", "_")
                related = neo4j_query(
                    """
                    MATCH (n)-[r]-(connected)
                    WHERE n.id CONTAINS $query
                    RETURN connected.name AS name, labels(connected) AS types,
                           type(r) AS rel_type, r.evidence AS evidence
                    LIMIT 5
                    """,
                    {"query": node_id[:50]},
                )
                if related:
                    neo4j_context[e["entity"]] = [
                        {"name": r.get("name", ""), "type": r.get("types", [""])[0] if r.get("types") else "",
                         "relation": r.get("rel_type", ""), "evidence": r.get("evidence", "")}
                        for r in related
                    ]
        except Exception:
            pass

    summary = (
        " | ".join(texts[:2])
        if texts
        else "No uploaded documents available yet."
    )

    return {
        "message": message,
        "summary": summary,
        "document_count": len(texts),
        "entities": [e["entity"] for e in unique_entities[:10]],
        "relationships": relationships,
        "neo4j_context": neo4j_context,
    }


def build_graph_enhanced_query(query: str, entities: list[dict]) -> str:
    entity_names = [e["entity"] for e in entities]
    entity_types = {e["entity"]: e["type"] for e in entities}

    context_parts = [f"Query: {query}"]

    if entity_names:
        context_parts.append(f"Entities: {', '.join(entity_names)}")

    equipment = [
        e["entity"]
        for e in entities
        if e["type"] == "EQUIPMENT"
    ]
    failures = [
        e["entity"]
        for e in entities
        if e["type"] == "FAILURE"
    ]

    if equipment and failures:
        context_parts.append(
            f"Graph context: {', '.join(equipment)} may have failures "
            f"({', '.join(failures)}) linked via FAILED_IN relationships."
        )

    if is_connected():
        try:
            related_lines = []
            for e in entities[:2]:
                nid = e["entity"].lower().replace(" ", "_")
                results = neo4j_query(
                    "MATCH (n)-[r]-(c) WHERE n.id CONTAINS $q RETURN c.name, type(r) LIMIT 3",
                    {"q": nid[:50]},
                )
                for row in results:
                    related_lines.append(f"{e['entity']} --[{row.get('type(r)', '?')}]--> {row.get('c.name', '?')}")
            if related_lines:
                context_parts.append("Neo4j graph: " + "; ".join(related_lines[:3]))
        except Exception:
            pass

    return " | ".join(context_parts)
