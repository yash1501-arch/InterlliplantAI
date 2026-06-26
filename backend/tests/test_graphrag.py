from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_response_includes_context_summary() -> None:
    client.post(
        "/api/documents/upload",
        files={"file": ("maintenance.txt", b"Pump inspection checklist\nCheck vibration and temperature", "text/plain")},
    )

    response = client.post(
        "/api/chat",
        json={"message": "What should I check on a pump?", "session_id": "graphrag-session"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "context" in payload
    assert payload["context"]["summary"]
