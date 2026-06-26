import asyncio
import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.api.auth.dependencies import require_role
from app.db.database import get_connection
from app.models.schemas import ChatRequest
from app.services.graph import log_activity
from app.services.langgraph_workflow import run_chat_workflow

router = APIRouter(dependencies=[Depends(require_role("viewer", "engineer", "admin"))])


@router.post("", response_model=None)
async def chat(payload: ChatRequest):
    if payload.stream:
        return StreamingResponse(
            _generate_chat_stream(payload),
            media_type="text/event-stream",
        )

    # Execute LangGraph workflow
    workflow_result = run_chat_workflow(payload.message)
    session_id = payload.session_id or str(uuid.uuid4())

    response_text = workflow_result["response"]

    # Persist to database
    with get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO chat_sessions (session_id) VALUES (?)", (session_id,))
        conn.execute(
            "INSERT INTO chat_messages (session_id, message, response) VALUES (?, ?, ?)",
            (session_id, payload.message, response_text),
        )
        conn.commit()

    log_activity("chat_message", f"Session {session_id}: {payload.message[:50]}")

    return {
        "message": payload.message,
        "response": response_text,
        "session_id": session_id,
        "agents": workflow_result["agents"],
        "context": {
            "intent": workflow_result["intent"],
            "retrieval": workflow_result["retrieval"],
        },
        "routing": {
            "intent": workflow_result["intent"],
            "agent_count": len(workflow_result["agents"]),
            "primary_agent": workflow_result["agents"][0] if workflow_result["agents"] else "supervisor",
            "confidence": workflow_result["confidence"],
        },
        "citations": workflow_result["citations"],
        "fusion": {
            "summary": response_text[:200],
            "insights": [f"{a} agent contributed" for a in workflow_result["agents"]],
        },
    }


async def _generate_chat_stream(payload: ChatRequest):
    """Stream the LangGraph workflow response word-by-word."""
    workflow_result = run_chat_workflow(payload.message)
    session_id = payload.session_id or str(uuid.uuid4())
    response_text = workflow_result["response"]

    words = response_text.split()
    for i, word in enumerate(words):
        chunk = word + (" " if i < len(words) - 1 else "")
        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk, 'session_id': session_id})}\n\n"
        await asyncio.sleep(0.02)

    with get_connection() as conn:
        conn.execute("INSERT OR IGNORE INTO chat_sessions (session_id) VALUES (?)", (session_id,))
        conn.execute(
            "INSERT INTO chat_messages (session_id, message, response) VALUES (?, ?, ?)",
            (session_id, payload.message, response_text),
        )
        conn.commit()

    yield f"data: {json.dumps({'type': 'done', 'session_id': session_id, 'response': response_text, 'agents': workflow_result['agents'], 'citations': workflow_result['citations'], 'routing': {'intent': workflow_result['intent'], 'confidence': workflow_result['confidence'], 'agent_count': len(workflow_result['agents'])}})}\n\n"


@router.get("/sessions")
def list_sessions() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT s.session_id, s.created_at,
                   (SELECT COUNT(*) FROM chat_messages m WHERE m.session_id = s.session_id) as message_count
            FROM chat_sessions s
            ORDER BY s.created_at DESC
            """
        ).fetchall()
    return [
        {
            "session_id": row["session_id"],
            "message_count": row["message_count"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


@router.get("/history/{session_id}")
def get_chat_history(session_id: str) -> list[dict]:
    with get_connection() as conn:
        session = conn.execute(
            "SELECT session_id FROM chat_sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        rows = conn.execute(
            "SELECT id, session_id, message, response, created_at FROM chat_messages WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "session_id": row["session_id"],
            "message": row["message"],
            "response": row["response"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


@router.delete("/history/{session_id}", dependencies=[Depends(require_role("admin"))])
def clear_chat_history(session_id: str) -> dict:
    with get_connection() as conn:
        session = conn.execute(
            "SELECT session_id FROM chat_sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        conn.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM chat_sessions WHERE session_id = ?", (session_id,))
        conn.commit()
    log_activity("chat_session_deleted", f"Session {session_id}")
    return {"message": "Chat session deleted", "session_id": session_id}


@router.get("/stream/{session_id}")
async def stream_chat(session_id: str):
    async def event_generator():
        with get_connection() as conn:
            session = conn.execute(
                "SELECT session_id FROM chat_sessions WHERE session_id = ?", (session_id,)
            ).fetchone()
            if not session:
                yield f"data: {json.dumps({'type': 'error', 'detail': 'Session not found'})}\n\n"
                return
            rows = conn.execute(
                "SELECT message, response, created_at FROM chat_messages WHERE session_id = ? ORDER BY id",
                (session_id,),
            ).fetchall()
            for row in rows:
                yield f"data: {json.dumps({'type': 'message', 'message': row['message'], 'response': row['response'], 'created_at': row['created_at']})}\n\n"
                await asyncio.sleep(0.05)
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
