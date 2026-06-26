from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_nonexistent_document_returns_404() -> None:
    response = client.get("/api/documents/nonexistent-doc-id-12345")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_delete_nonexistent_document_returns_404() -> None:
    response = client.delete("/api/documents/nonexistent-doc-id-12345")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_chat_with_empty_message_succeeds() -> None:
    response = client.post(
        "/api/chat",
        json={"message": "", "session_id": "error-empty-msg"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["response"]


def test_search_with_empty_query_returns_empty_results() -> None:
    response = client.post("/api/search", json={"query": ""})
    assert response.status_code == 200
    payload = response.json()
    assert payload["results"] == []


def test_chat_with_missing_message_field_returns_422() -> None:
    response = client.post("/api/chat", json={})
    assert response.status_code == 422


def test_search_with_missing_query_field_returns_422() -> None:
    response = client.post("/api/search", json={})
    assert response.status_code == 422


def test_chat_with_none_message_returns_422() -> None:
    response = client.post("/api/chat", json={"message": None})
    assert response.status_code == 422


def test_upload_with_no_file_returns_422() -> None:
    response = client.post("/api/documents/upload")
    assert response.status_code == 422


def test_upload_with_empty_file() -> None:
    response = client.post(
        "/api/documents/upload",
        files={"file": ("empty.txt", b"", "text/plain")},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "uploaded"
    assert payload["size"] == 0


def test_upload_unsupported_file_type_returns_400() -> None:
    response = client.post(
        "/api/documents/upload",
        files={"file": ("script.exe", b"fake binary content", "application/octet-stream")},
    )
    assert response.status_code == 400
    assert "unsupported file type" in response.json()["detail"].lower()


def test_search_with_long_query() -> None:
    long_query = "pump " * 500
    response = client.post("/api/search", json={"query": long_query.strip()})
    assert response.status_code == 200


def test_chat_with_long_message() -> None:
    long_message = "maintenance " * 500
    response = client.post(
        "/api/chat",
        json={"message": long_message.strip(), "session_id": "error-long-msg"},
    )
    assert response.status_code == 200
    assert response.json()["response"]


def test_get_dashboard_metrics() -> None:
    response = client.get("/api/dashboard/metrics")
    assert response.status_code == 200
    payload = response.json()
    assert "documents" in payload
    assert "sessions" in payload
    assert "messages" in payload


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
