import uuid
from dataclasses import dataclass, field
from typing import Any

from app.services.chunking import chunk_text
from app.services.ocr import extract_text_and_metadata
from app.services.vector_store import index_chunks


@dataclass
class IngestionResult:
    file_id: str
    filename: str
    status: str = "queued"
    chunks: list[dict[str, Any]] = field(default_factory=list)


def queue_ingestion(filename: str) -> IngestionResult:
    return IngestionResult(file_id=str(uuid.uuid4()), filename=filename, status="queued")


def process_document(file_id: str, filename: str, content: bytes) -> dict[str, Any]:
    result = extract_text_and_metadata(filename, content)
    chunks = chunk_text(result.text)
    indexed = 0
    try:
        indexed = index_chunks(chunks, document_id=file_id)
    except Exception:
        pass
    return {
        "file_id": file_id,
        "filename": filename,
        "text": result.text,
        "metadata": result.metadata,
        "chunks": chunks,
        "embedding_status": "indexed" if indexed > 0 else "skipped",
    }
