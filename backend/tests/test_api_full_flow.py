import sqlite3
import uuid

from fastapi.testclient import TestClient

from app.db.database import get_db_path
from app.main import app

client = TestClient(app)


import uuid


def test_full_user_flow() -> None:
    suffix = uuid.uuid4().hex[:8]
    email = f"flowuser_{suffix}@test.com"
    password = "Pass1234"

    register = client.post(
        "/api/auth/register",
        json={"name": "Flow User", "email": email, "password": password},
    )
    assert register.status_code == 200
    user_id = register.json()["id"]

    login = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["id"] == user_id

    upload = client.post(
        "/api/documents/upload",
        files={"file": ("sop_pump.txt", b"Pump maintenance procedure: inspect impeller, check seals, verify alignment.", "text/plain")},
    )
    assert upload.status_code == 200
    file_id = upload.json()["file_id"]

    search = client.post("/api/search", json={"query": "pump impeller inspection"})
    assert search.status_code == 200
    search_data = search.json()
    assert len(search_data["results"]) > 0
    assert any(r["id"] == file_id for r in search_data["results"])

    session_id = f"full-flow-{uuid.uuid4().hex[:8]}"

    chat = client.post(
        "/api/chat",
        json={"message": "What does the SOP say about pump impeller inspection?", "session_id": session_id},
    )
    assert chat.status_code == 200
    chat_data = chat.json()
    assert chat_data["response"]
    assert chat_data["session_id"] == session_id

    with sqlite3.connect(get_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        doc_row = conn.execute("SELECT id FROM documents WHERE id = ?", (file_id,)).fetchone()
        chat_rows = conn.execute("SELECT session_id FROM chat_sessions WHERE session_id = ?", (session_id,)).fetchall()
        msg_rows = conn.execute("SELECT message FROM chat_messages WHERE session_id = ?", (session_id,)).fetchall()

    assert doc_row is not None
    assert len(chat_rows) == 1
    assert len(msg_rows) >= 1
    assert any("pump" in r["message"].lower() for r in msg_rows)


def test_multi_turn_chat_session() -> None:
    session_id = f"multi-turn-{uuid.uuid4().hex[:8]}"

    turn1 = client.post("/api/chat", json={"message": "Tell me about pump maintenance", "session_id": session_id})
    assert turn1.status_code == 200
    t1 = turn1.json()
    assert t1["session_id"] == session_id

    turn2 = client.post("/api/chat", json={"message": "What about motor bearing replacement?", "session_id": session_id})
    assert turn2.status_code == 200
    t2 = turn2.json()
    assert t2["session_id"] == session_id

    turn3 = client.post("/api/chat", json={"message": "Summarize the compliance requirements", "session_id": session_id})
    assert turn3.status_code == 200
    t3 = turn3.json()
    assert t3["session_id"] == session_id

    with sqlite3.connect(get_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        messages = conn.execute(
            "SELECT message, response FROM chat_messages WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()

    assert len(messages) == 3
    assert "pump" in messages[0]["message"].lower()
    assert "motor" in messages[1]["message"].lower()


def test_upload_delete_verify_gone() -> None:
    upload = client.post(
        "/api/documents/upload",
        files={"file": ("delete_me.txt", b"This document will be deleted.", "text/plain")},
    )
    assert upload.status_code == 200
    file_id = upload.json()["file_id"]

    get_before = client.get(f"/api/documents/{file_id}")
    assert get_before.status_code == 200

    delete = client.delete(f"/api/documents/{file_id}")
    assert delete.status_code == 200
    assert delete.json()["message"] == "Document deleted successfully"

    with sqlite3.connect(get_db_path()) as conn:
        row = conn.execute("SELECT id FROM documents WHERE id = ?", (file_id,)).fetchone()
    assert row is None


def test_upload_multiple_docs_verify_list_count() -> None:
    upload1 = client.post(
        "/api/documents/upload",
        files={"file": ("multi_1.txt", b"Document one content for testing.", "text/plain")},
    )
    assert upload1.status_code == 200
    id1 = upload1.json()["file_id"]

    upload2 = client.post(
        "/api/documents/upload",
        files={"file": ("multi_2.txt", b"Document two content for testing.", "text/plain")},
    )
    assert upload2.status_code == 200
    id2 = upload2.json()["file_id"]

    upload3 = client.post(
        "/api/documents/upload",
        files={"file": ("multi_3.txt", b"Document three content for testing.", "text/plain")},
    )
    assert upload3.status_code == 200
    id3 = upload3.json()["file_id"]

    list_response = client.get("/api/documents")
    assert list_response.status_code == 200
    docs = list_response.json()
    found_ids = {d["id"] for d in docs}
    assert id1 in found_ids
    assert id2 in found_ids
    assert id3 in found_ids

    for doc in docs:
        if doc["id"] in (id1, id2, id3):
            assert doc["status"] == "uploaded"
            assert doc["preview"]


def test_chat_session_persistence() -> None:
    session_id = f"persistence-{uuid.uuid4().hex[:8]}"

    client.post(
        "/api/chat",
        json={"message": "Hello persistence test", "session_id": session_id},
    )
    client.post(
        "/api/chat",
        json={"message": "Second message in same session", "session_id": session_id},
    )

    with sqlite3.connect(get_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        session = conn.execute("SELECT session_id FROM chat_sessions WHERE session_id = ?", (session_id,)).fetchone()
        messages = conn.execute(
            "SELECT message FROM chat_messages WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()

    assert session is not None
    assert len(messages) == 2
    assert messages[0]["message"] == "Hello persistence test"
    assert messages[1]["message"] == "Second message in same session"


def test_dashboard_metrics_reflect_uploads() -> None:
    metrics_before = client.get("/api/dashboard/metrics")
    assert metrics_before.status_code == 200
    docs_before = metrics_before.json()["documents"]

    client.post(
        "/api/documents/upload",
        files={"file": ("metrics_test.txt", b"Dashboard metrics test document.", "text/plain")},
    )

    metrics_after = client.get("/api/dashboard/metrics")
    assert metrics_after.status_code == 200
    assert metrics_after.json()["documents"] >= docs_before + 1
