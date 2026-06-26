from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_domain_specific_chat_routes_are_supported() -> None:
    response = client.post(
        "/api/chat",
        json={"message": "Perform RCA for a pump failure", "session_id": "domain-session"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "rca" in payload["response"].lower()
