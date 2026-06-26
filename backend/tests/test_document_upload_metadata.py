import json

from fastapi.testclient import TestClient

from app.db.database import get_connection
from app.main import app


client = TestClient(app)


def test_upload_document_persists_rich_metadata() -> None:
    response = client.post(
        "/api/documents/upload",
        files={"file": ("report.txt", b"Pump Inspection Report\nEquipment: Pump A\nStatus: Healthy", "text/plain")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["file_id"]

    with get_connection() as conn:
        row = conn.execute(
            "SELECT metadata FROM document_texts WHERE document_id = ?",
            (payload["file_id"],),
        ).fetchone()
    assert row is not None
    metadata = json.loads(row[0])
    assert metadata["filename"] == "report.txt"
    assert metadata["section_count"] >= 1
