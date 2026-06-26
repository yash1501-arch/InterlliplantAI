import sqlite3

from fastapi.testclient import TestClient

from app.db.database import get_db_path, init_db
from app.main import app


client = TestClient(app)


def test_upload_and_chat_are_persisted() -> None:
    init_db()

    upload_response = client.post(
        "/api/documents/upload",
        files={"file": ("maintenance.pdf", b"Pump inspection checklist", "application/pdf")},
    )
    assert upload_response.status_code == 200
    payload = upload_response.json()
    assert payload["status"] == "uploaded"

    documents_response = client.get("/api/documents")
    assert documents_response.status_code == 200
    documents = documents_response.json()
    assert any(item["id"] == payload["file_id"] for item in documents)

    chat_response = client.post(
        "/api/chat",
        json={"message": "How do I inspect a pump?", "session_id": "session-1"},
    )
    assert chat_response.status_code == 200

    with sqlite3.connect(get_db_path()) as conn:
        document_row = conn.execute("SELECT id FROM documents WHERE id = ?", (payload["file_id"],)).fetchone()
        chat_row = conn.execute("SELECT session_id FROM chat_sessions WHERE session_id = ?", ("session-1",)).fetchone()

    assert document_row is not None
    assert chat_row is not None
