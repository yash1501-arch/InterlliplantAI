from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_entity_extraction_identifies_key_terms() -> None:
    client.post(
        "/api/documents/upload",
        files={"file": ("maintenance.txt", b"Pump inspection checklist\nCheck vibration and temperature", "text/plain")},
    )

    response = client.post(
        "/api/chat",
        json={"message": "What should I check on a pump?", "session_id": "entity-session"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["context"]["entities"]
    assert any("pump" in entity.lower() for entity in payload["context"]["entities"])
