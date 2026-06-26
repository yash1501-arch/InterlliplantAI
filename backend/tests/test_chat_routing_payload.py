from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_response_includes_routing_details() -> None:
    response = client.post(
        "/api/chat",
        json={"message": "Investigate a pump failure with RCA", "session_id": "routing-session"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["routing"]["agent_count"] >= 2
    assert payload["routing"]["primary_agent"]
