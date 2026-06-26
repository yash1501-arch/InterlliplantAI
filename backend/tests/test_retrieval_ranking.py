from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_search_returns_ranked_results() -> None:
    client.post(
        "/api/documents/upload",
        files={"file": ("inspection.txt", b"Pump inspection checklist for maintenance", "text/plain")},
    )
    client.post(
        "/api/documents/upload",
        files={"file": ("rca.txt", b"Root cause analysis summary for incident review", "text/plain")},
    )

    response = client.post("/api/search", json={"query": "pump inspection"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["results"]
    assert payload["results"][0]["title"] == "inspection.txt"
