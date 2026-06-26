import json
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth.routes import router as auth_router
from app.api.documents.routes import router as documents_router
from app.api.search.routes import router as search_router
from app.api.chat.routes import router as chat_router
from app.api.rca.routes import router as rca_router
from app.api.compliance.routes import router as compliance_router
from app.api.lessons.routes import router as lessons_router
from app.api.graph.routes import router as graph_router
from app.api.dashboard.routes import router as dashboard_router
from app.db.database import init_db


@asynccontextmanager
async def lifespan(application: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="IntelliPlant AI",
    version="1.0.0",
    description="AI-Powered Industrial Knowledge Intelligence Platform",
    lifespan=lifespan,
)

API_PREFIX = "/api/v1"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=f"{API_PREFIX}/auth", tags=["auth"])
app.include_router(documents_router, prefix=f"{API_PREFIX}/documents", tags=["documents"])
app.include_router(search_router, prefix=f"{API_PREFIX}/search", tags=["search"])
app.include_router(chat_router, prefix=f"{API_PREFIX}/chat", tags=["chat"])
app.include_router(rca_router, prefix=f"{API_PREFIX}/rca", tags=["rca"])
app.include_router(compliance_router, prefix=f"{API_PREFIX}/compliance", tags=["compliance"])
app.include_router(lessons_router, prefix=f"{API_PREFIX}/lessons", tags=["lessons"])
app.include_router(graph_router, prefix=f"{API_PREFIX}/graph", tags=["graph"])
app.include_router(dashboard_router, prefix=f"{API_PREFIX}/dashboard", tags=["dashboard"])

# Also keep legacy /api/ routes for backwards compatibility
app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
app.include_router(search_router, prefix="/api/search", tags=["search"])
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
app.include_router(rca_router, prefix="/api/rca", tags=["rca"])
app.include_router(compliance_router, prefix="/api/compliance", tags=["compliance"])
app.include_router(lessons_router, prefix="/api/lessons", tags=["lessons"])
app.include_router(graph_router, prefix="/api/graph", tags=["graph"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])


@app.get("/health")
def health_check() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "intelliplant-ai",
        "features": [
            "auth", "documents", "search", "chat",
            "rca", "compliance", "lessons", "graph", "dashboard",
        ],
    }


@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket) -> None:
    await websocket.accept()
    session_id = str(uuid.uuid4())
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data).get("message", "")
            from app.agents.supervisor import build_supervisor_response
            from app.services.fusion import build_fused_response
            from app.services.orchestrator import build_agent_plan
            from app.services.graphrag import build_context_summary
            from app.db.database import get_connection

            supervisor_response = build_supervisor_response(message)
            context_summary = build_context_summary(message)
            agent_plan = build_agent_plan(message)
            fused_response = build_fused_response(message, agent_plan)
            response_text = f"{supervisor_response['response']} {fused_response['summary']}"

            with get_connection() as conn:
                conn.execute(
                    "INSERT OR IGNORE INTO chat_sessions (session_id) VALUES (?)",
                    (session_id,),
                )
                conn.execute(
                    "INSERT INTO chat_messages (session_id, message, response) VALUES (?, ?, ?)",
                    (session_id, message, response_text),
                )
                conn.commit()

            await websocket.send_json({
                "message": message,
                "response": response_text,
                "session_id": session_id,
                "agents": agent_plan,
                "context": context_summary,
                "fusion": fused_response,
            })
    except WebSocketDisconnect:
        pass
