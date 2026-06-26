from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_multi_agent_orchestration_returns_agent_plan() -> None:
    response = client.post(
        "/api/chat",
        json={"message": "Investigate a pump failure with RCA and compliance review", "session_id": "multi-agent-session"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["agents"]
    assert len(payload["agents"]) >= 2
