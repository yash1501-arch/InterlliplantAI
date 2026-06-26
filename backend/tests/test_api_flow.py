from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_search_and_chat_flow() -> None:
    upload_response = client.post(
        "/api/documents/upload",
        files={"file": ("sop.txt", b"Maintenance procedure for pump inspection and safety checks.", "text/plain")},
    )
    assert upload_response.status_code == 200
    payload = upload_response.json()
    assert payload["status"] == "uploaded"

    search_response = client.post(
        "/api/search",
        json={"query": "pump inspection"},
    )
    assert search_response.status_code == 200
    search_payload = search_response.json()
    assert search_payload["results"]

    chat_response = client.post(
        "/api/chat",
        json={"message": "What does the maintenance guide say about pump inspection?"},
    )
    assert chat_response.status_code == 200
    chat_payload = chat_response.json()
    assert "pump" in chat_payload["response"].lower()
