import json
import uuid

from app.db.database import get_connection
from app.services.entities import extract_entities


def extract_lessons(equipment: str | None = None, query: str | None = None) -> dict[str, object]:
    with get_connection() as conn:
        rows = conn.execute("SELECT text, metadata FROM document_texts").fetchall()
    texts = [row["text"] for row in rows if row["text"]]
    combined = " ".join(texts)
    entities = extract_entities(combined)

    patterns = []
    actions = []

    if any(term in combined.lower() for term in ["failure", "incident", "breakdown"]):
        patterns.append({
            "pattern": "Equipment failure due to inadequate preventive maintenance",
            "frequency": "high" if combined.lower().count("failure") > 2 else "medium",
            "severity": "high",
        })
        actions.append("Implement predictive maintenance schedule based on OEM recommendations.")
        actions.append("Create a cross-functional review team for repeated failure modes.")

    if any(term in combined.lower() for term in ["near miss", "close call"]):
        patterns.append({
            "pattern": "Near-miss events indicating latent safety gaps",
            "frequency": "medium",
            "severity": "medium",
        })
        actions.append("Conduct root cause analysis on near-miss events.")
        actions.append("Update safety procedures and conduct refresher training.")

    if not patterns:
        patterns.append({
            "pattern": "No significant incident patterns detected from ingested documents",
            "frequency": "unknown",
            "severity": "low",
        })
        actions.append("Continue routine monitoring and document ingestion.")

    lesson_id = str(uuid.uuid4())
    result_data = json.dumps({
        "equipment": equipment,
        "patterns": patterns,
        "actions": actions,
        "entities_found": [e["entity"] for e in entities[:8]],
        "source_count": len(texts),
    })

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO lessons_learned (id, equipment, query, result) VALUES (?, ?, ?, ?)",
            (lesson_id, equipment, query, result_data),
        )
        conn.commit()

    return {
        "id": lesson_id,
        "equipment": equipment,
        "patterns": patterns,
        "actions": actions,
        "entities_found": [e["entity"] for e in entities[:8]],
        "source_count": len(texts),
    }


def list_lessons() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, equipment, query, result, created_at FROM lessons_learned ORDER BY created_at DESC"
        ).fetchall()

    lessons = []
    for row in rows:
        try:
            result_data = json.loads(row["result"])
        except (json.JSONDecodeError, TypeError):
            result_data = {}
        lessons.append({
            "id": row["id"],
            "equipment": result_data.get("equipment"),
            "patterns": result_data.get("patterns", []),
            "actions": result_data.get("actions", []),
            "entities_found": result_data.get("entities_found", []),
            "source_count": result_data.get("source_count", 0),
            "created_at": row["created_at"],
        })
    return lessons


def get_recurring_patterns() -> list[dict]:
    lessons = list_lessons()
    pattern_count: dict[str, dict] = {}
    for lesson in lessons:
        for p in lesson.get("patterns", []):
            key = p.get("pattern", "")
            if key in pattern_count:
                pattern_count[key]["count"] += 1
            else:
                pattern_count[key] = {
                    "pattern": key,
                    "frequency": p.get("frequency", "unknown"),
                    "severity": p.get("severity", "low"),
                    "count": 1,
                }
    return sorted(pattern_count.values(), key=lambda x: x["count"], reverse=True)
