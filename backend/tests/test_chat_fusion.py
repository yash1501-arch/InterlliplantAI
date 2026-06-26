from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_chat_response_includes_fused_insights() -> None:
    response = client.post(
        "/api/chat",
        json={"message": "Investigate a pump failure with RCA and compliance review", "session_id": "fusion-session"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["fusion"]["insights"]
    assert any("RCA" in insight for insight in payload["fusion"]["insights"])
