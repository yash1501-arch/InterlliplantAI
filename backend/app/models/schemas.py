from pydantic import BaseModel
from typing import Any


class UserOut(BaseModel):
    id: str
    email: str
    name: str
    role: str


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserOut


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class SearchFilters(BaseModel):
    file_type: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    status: str | None = None


class SearchRequest(BaseModel):
    query: str
    page: int = 1
    page_size: int = 20
    filters: SearchFilters | None = None


class SearchResultItem(BaseModel):
    id: str
    title: str
    snippet: str
    score: float
    matched_entities: list[str]
    document_name: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    stream: bool = False


class ChatSessionInfo(BaseModel):
    session_id: str
    message_count: int
    created_at: str


class ChatMessageInfo(BaseModel):
    id: int
    session_id: str
    message: str
    response: str
    created_at: str


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    size: int
    content_type: str
    status: str
    message: str


class RCARequest(BaseModel):
    equipment: str


class RCADetail(BaseModel):
    id: str
    equipment: str
    root_cause: str
    failure_modes: list[str]
    recommendations: list[str]
    created_at: str | None = None


class RCAHistoryItem(BaseModel):
    id: str
    equipment: str
    created_at: str


class ComplianceCheckRequest(BaseModel):
    document_id: str | None = None
    query: str | None = None


class ComplianceResult(BaseModel):
    document_id: str | None
    violations: list[dict[str, Any]]
    recommendations: list[str]
    summary: str
    standards_checked: list[str]


class ComplianceHistoryItem(BaseModel):
    id: str
    document_id: str | None
    query: str | None
    summary: str
    created_at: str


class LessonsRequest(BaseModel):
    equipment: str | None = None
    query: str | None = None


class LessonResultItem(BaseModel):
    id: str
    equipment: str | None
    patterns: list[dict[str, Any]]
    actions: list[str]
    entities_found: list[str]
    source_count: int
    created_at: str | None = None


class GraphStats(BaseModel):
    total_nodes: int
    total_edges: int
    node_types: dict[str, int]
    document_count: int


class GraphSearchResult(BaseModel):
    id: str
    label: str
    type: str
    group: str
    context: str


class TrendPoint(BaseModel):
    date: str
    value: int | float
    metric: str


class ActivityEntry(BaseModel):
    id: int
    action: str
    detail: str
    created_at: str
