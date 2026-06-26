from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_list_documents_returns_metadata_and_preview() -> None:
    response = client.post(
        "/api/documents/upload",
        files={"file": ("report.txt", b"Pump Inspection Report\nEquipment: Pump A\nStatus: Healthy", "text/plain")},
    )
    assert response.status_code == 200

    list_response = client.get("/api/documents")
    assert list_response.status_code == 200
    payload = list_response.json()
    assert payload

    match = next(item for item in payload if item["name"] == "report.txt")
    assert "preview" in match
    assert "metadata" in match
    assert match["metadata"]["filename"] == "report.txt"
