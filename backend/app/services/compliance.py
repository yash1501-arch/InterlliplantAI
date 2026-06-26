import json
import uuid

from app.db.database import get_connection


STANDARDS = ["OISD", "ISO 9001", "Factory Act", "PESO"]

COMPLIANCE_CHECKS = {
    "OISD": ["safety", "pressure", "relief valve"],
    "ISO 9001": ["procedure", "document control", "audit"],
    "Factory Act": ["working hours", "safety equipment", "training"],
    "PESO": ["explosive", "storage", "license", "safety distance"],
}


def check_compliance(document_id: str | None = None, query: str | None = None) -> dict[str, object]:
    with get_connection() as conn:
        if document_id:
            rows = conn.execute(
                "SELECT text, metadata FROM document_texts WHERE document_id = ?",
                (document_id,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT text, metadata FROM document_texts").fetchall()

    texts = [row["text"] for row in rows if row["text"]]
    combined = " ".join(texts)

    violations = []
    recommendations = []

    for standard, keywords in COMPLIANCE_CHECKS.items():
        matched = [kw for kw in keywords if kw in combined.lower()]
        if not matched or len(matched) < 2:
            violations.append({
                "standard": standard,
                "status": "insufficient_evidence",
                "detail": f"Missing or insufficient references to {', '.join(keywords)} in ingested documents.",
            })
            recommendations.append(f"Review and update documentation for {standard} compliance.")
        else:
            violations.append({
                "standard": standard,
                "status": "partial_coverage",
                "detail": f"Found references to {', '.join(matched)}.",
            })
            recommendations.append(f"Continue monitoring {standard} compliance — partial coverage detected.")

    summary = f"Checked {len(texts)} document(s) against {len(COMPLIANCE_CHECKS)} regulatory standards."

    check_id = str(uuid.uuid4())
    result_data = json.dumps({
        "document_id": document_id or "all",
        "violations": violations,
        "recommendations": recommendations,
        "summary": summary,
        "standards_checked": STANDARDS,
    })

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO compliance_checks (id, document_id, query, result) VALUES (?, ?, ?, ?)",
            (check_id, document_id, query, result_data),
        )
        conn.commit()

    return {
        "document_id": document_id or "all",
        "violations": violations,
        "recommendations": recommendations,
        "summary": summary,
        "standards_checked": STANDARDS,
    }


def get_compliance_history() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, document_id, query, result, created_at FROM compliance_checks ORDER BY created_at DESC LIMIT 50"
        ).fetchall()

    history = []
    for row in rows:
        try:
            result_data = json.loads(row["result"])
        except (json.JSONDecodeError, TypeError):
            result_data = {}
        history.append({
            "id": row["id"],
            "document_id": row["document_id"],
            "query": row["query"],
            "summary": result_data.get("summary", ""),
            "created_at": row["created_at"],
        })
    return history


def get_available_standards() -> list[dict]:
    return [
        {"id": s.lower().replace(" ", "_"), "name": s, "keywords": COMPLIANCE_CHECKS[s]}
        for s in STANDARDS
    ]
