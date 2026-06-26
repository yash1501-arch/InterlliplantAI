from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_search_uses_extracted_document_text() -> None:
    client.post(
        "/api/documents/upload",
        files={"file": ("maintenance.txt", b"Pump inspection checklist\nVerify vibration and temperature", "text/plain")},
    )

    response = client.post("/api/search", json={"query": "vibration"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["results"]
    assert "vibration" in payload["results"][0]["snippet"].lower()
