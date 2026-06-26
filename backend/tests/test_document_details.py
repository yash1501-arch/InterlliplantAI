from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_get_document_returns_text_and_metadata() -> None:
    upload_response = client.post(
        "/api/documents/upload",
        files={"file": ("report.txt", b"Pump Inspection Report\nEquipment: Pump A", "text/plain")},
    )
    assert upload_response.status_code == 200
    file_id = upload_response.json()["file_id"]

    response = client.get(f"/api/documents/{file_id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == file_id
    assert payload["text"]
    assert payload["metadata"]["filename"] == "report.txt"
