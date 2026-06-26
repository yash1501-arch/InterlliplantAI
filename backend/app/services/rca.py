import json
import uuid

from app.db.database import get_connection


def perform_rca_analysis(equipment: str) -> dict[str, object]:
    with get_connection() as conn:
        rows = conn.execute("SELECT text FROM document_texts").fetchall()
    texts = [row["text"] for row in rows if row["text"]]
    combined = " ".join(texts)

    failure_modes = []
    if any(term in combined.lower() for term in ["vibration", "cavitation", "bearing"]):
        failure_modes.append("Mechanical wear / bearing degradation")
    if any(term in combined.lower() for term in ["temperature", "overheating", "thermal"]):
        failure_modes.append("Thermal overload")
    if any(term in combined.lower() for term in ["leak", "leakage", "seal"]):
        failure_modes.append("Seal / gasket failure")
    if not failure_modes:
        failure_modes = ["Unknown — insufficient data in ingested documents"]

    recommendations = [
        "Review maintenance logs for recurring patterns",
        "Schedule vibration analysis",
        "Check lubrication and alignment",
        "Verify operating parameters against OEM specs",
    ]

    root_cause = (
        f"Root cause analysis for {equipment}: "
        f"identified potential failure modes — {'; '.join(failure_modes)}. "
        "Recommended actions: inspect related subsystems, review maintenance history, "
        "and schedule condition monitoring."
    )

    rca_id = str(uuid.uuid4())
    result_data = json.dumps({
        "equipment": equipment,
        "root_cause": root_cause,
        "failure_modes": failure_modes,
        "recommendations": recommendations,
    })

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO rca_results (id, equipment, result) VALUES (?, ?, ?)",
            (rca_id, equipment, result_data),
        )
        conn.commit()

    return {
        "id": rca_id,
        "equipment": equipment,
        "root_cause": root_cause,
        "failure_modes": failure_modes,
        "recommendations": recommendations,
    }


def get_rca_history() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, equipment, result, created_at FROM rca_results ORDER BY created_at DESC"
        ).fetchall()

    history = []
    for row in rows:
        try:
            result_data = json.loads(row["result"])
        except (json.JSONDecodeError, TypeError):
            result_data = {}
        history.append({
            "id": row["id"],
            "equipment": result_data.get("equipment", row["equipment"]),
            "created_at": row["created_at"],
        })
    return history


def get_rca_detail(rca_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, equipment, result, created_at FROM rca_results WHERE id = ?",
            (rca_id,),
        ).fetchone()

    if not row:
        return None

    try:
        result_data = json.loads(row["result"])
    except (json.JSONDecodeError, TypeError):
        result_data = {}

    return {
        "id": row["id"],
        "equipment": row["equipment"],
        "root_cause": result_data.get("root_cause", ""),
        "failure_modes": result_data.get("failure_modes", []),
        "recommendations": result_data.get("recommendations", []),
        "created_at": row["created_at"],
    }
