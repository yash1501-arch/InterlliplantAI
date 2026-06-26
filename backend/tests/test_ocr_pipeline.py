from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_ocr_pipeline_extracts_text_from_upload() -> None:
    response = client.post(
        "/api/documents/upload",
        files={"file": ("maintenance.txt", b"Pump inspection checklist\nCheck vibration and temperature", "text/plain")},
    )
    assert response.status_code == 200

    ocr_response = client.get("/api/documents")
    assert ocr_response.status_code == 200
    documents = ocr_response.json()
    assert documents

    first_document = documents[0]
    assert first_document["name"]
