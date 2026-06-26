import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_login_and_protected_endpoint() -> None:
    login_response = client.post(
        "/api/auth/login",
        json={"email": "admin@intelliplant.ai", "password": "password123"},
    )
    assert login_response.status_code == 200
    payload = login_response.json()
    assert payload["access_token"]

    protected_response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {payload['access_token']}"},
    )
    assert protected_response.status_code == 200
    assert protected_response.json()["email"] == "admin@intelliplant.ai"


def test_login_wrong_password_returns_401() -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@intelliplant.ai", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_login_nonexistent_user_returns_401() -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "nobody@nowhere.com", "password": "irrelevant"},
    )
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]


def test_invalid_token_returns_401() -> None:
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer thisisatotallyinvalidtoken"},
    )
    assert response.status_code == 401


def test_expired_malformed_token_returns_401() -> None:
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbkBpbnRlbGxpcGxhbnQuYWkifQ.invalidsig"},
    )
    assert response.status_code == 401


def test_no_token_returns_401() -> None:
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_register_missing_fields_returns_422() -> None:
    response = client.post("/api/auth/register", json={})
    assert response.status_code == 422


def test_register_partial_fields_returns_422() -> None:
    response = client.post("/api/auth/register", json={"name": "Partial"})
    assert response.status_code == 422

    response = client.post("/api/auth/register", json={"email": "partial@test.com"})
    assert response.status_code == 422

def test_register_then_login_flow() -> None:
    suffix = uuid.uuid4().hex[:8]
    email = f"flowtest_{suffix}@intelliplant.ai"
    name = "Flow Tester"
    password = "securePass123"

    reg = client.post(
        "/api/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    assert reg.status_code == 200
    reg_data = reg.json()
    assert reg_data["email"] == email

    login = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    login_data = login.json()
    assert login_data["access_token"]
    assert login_data["user"]["email"] == email
    assert login_data["user"]["name"] == name


def test_register_duplicate_email_returns_400() -> None:
    suffix = uuid.uuid4().hex[:8]
    email = f"duptest_{suffix}@intelliplant.ai"
    client.post(
        "/api/auth/register",
        json={"name": "Original", "email": email, "password": "pass123"},
    )
    response = client.post(
        "/api/auth/register",
        json={"name": "Dup", "email": email, "password": "irrelevant"},
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()
