import json

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.auth.dependencies import require_role
from app.db.database import get_connection
from app.models.schemas import UploadResponse
from app.services.entities import extract_entities
from app.services.ingestion import process_document, queue_ingestion
from app.services.neo4j_service import build_graph_from_entities, is_connected, save_document_node
from app.services.ocr import extract_text_and_metadata
from app.services.relationships import extract_relationships

router = APIRouter(dependencies=[Depends(require_role("viewer", "engineer", "admin"))])


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)) -> UploadResponse:
    content = await file.read()
    ingestion_result = queue_ingestion(file.filename or "upload.bin")
    try:
        ocr_result = extract_text_and_metadata(file.filename or "upload.bin", content)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO documents (id, filename, content_type, size, status) VALUES (?, ?, ?, ?, ?)",
            (ingestion_result.file_id, file.filename or "upload.bin", file.content_type or "application/octet-stream", len(content), "processing"),
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS document_texts (id TEXT PRIMARY KEY, document_id TEXT NOT NULL, text TEXT NOT NULL, metadata TEXT NOT NULL)",
        )
        conn.execute(
            "INSERT INTO document_texts (id, document_id, text, metadata) VALUES (?, ?, ?, ?)",
            (ingestion_result.file_id, ingestion_result.file_id, ocr_result.text, json.dumps(ocr_result.metadata)),
        )
        conn.commit()

    # Full ingestion pipeline: chunk → embed → index in Qdrant
    ingestion_status = "uploaded"
    try:
        result = process_document(ingestion_result.file_id, file.filename or "upload.bin", content)
        if result.get("embedding_status") == "indexed":
            ingestion_status = "completed"
        else:
            ingestion_status = "uploaded"
    except Exception:
        ingestion_status = "uploaded"

    # Build knowledge graph
    if is_connected():
        save_document_node(ingestion_result.file_id, file.filename or "upload.bin")

    entities = extract_entities(ocr_result.text)
    relationships = extract_relationships(entities, ocr_result.text)
    if is_connected():
        build_graph_from_entities(entities, relationships, document_id=ingestion_result.file_id)

    # Update status
    with get_connection() as conn:
        conn.execute("UPDATE documents SET status = ? WHERE id = ?", (ingestion_status, ingestion_result.file_id))
        conn.commit()

    return UploadResponse(
        file_id=ingestion_result.file_id,
        filename=file.filename or "upload.bin",
        size=len(content),
        content_type=file.content_type or "application/octet-stream",
        status=ingestion_status,
        message=f"Document processed. Embedding: {ingestion_status}. Entities: {len(entities)} extracted.",
    )


@router.post("/reindex")
def reindex_all_documents() -> dict:
    """Reindex all existing documents into Qdrant vector store."""
    from app.services.chunking import chunk_text
    from app.services.vector_store import index_chunks

    with get_connection() as conn:
        rows = conn.execute(
            "SELECT d.id, d.filename, dt.text FROM documents d JOIN document_texts dt ON dt.document_id = d.id"
        ).fetchall()

    total_indexed = 0
    total_docs = 0
    errors = []

    for row in rows:
        if not row["text"]:
            continue
        total_docs += 1
        try:
            chunks = chunk_text(row["text"])
            indexed = index_chunks(chunks, document_id=row["id"])
            total_indexed += indexed
        except Exception as e:
            errors.append(f"{row['filename']}: {str(e)}")

    with get_connection() as conn:
        conn.execute("UPDATE documents SET status = 'completed' WHERE id IN (SELECT document_id FROM document_texts WHERE text IS NOT NULL AND text != '')")
        conn.commit()

    return {
        "message": f"Reindexed {total_docs} documents, {total_indexed} chunks indexed to Qdrant",
        "documents_processed": total_docs,
        "chunks_indexed": total_indexed,
        "errors": errors[:10],
    }


@router.get("/{document_id}")
def get_document(document_id: str) -> dict:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT d.id, d.filename AS name, d.status, d.size, dt.text, dt.metadata
            FROM documents d
            LEFT JOIN document_texts dt ON dt.document_id = d.id
            WHERE d.id = ?
            """,
            (document_id,),
        ).fetchone()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    metadata_raw = row["metadata"] if row["metadata"] else "{}"
    try:
        metadata = json.loads(metadata_raw)
    except (TypeError, json.JSONDecodeError):
        metadata = {}

    return {
        "id": row["id"],
        "name": row["name"],
        "status": row["status"],
        "size": row["size"],
        "text": row["text"] or "",
        "metadata": metadata,
    }


@router.get("")
def list_documents() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT d.id, d.filename AS name, d.status, d.size, dt.text, dt.metadata
            FROM documents d
            LEFT JOIN document_texts dt ON dt.document_id = d.id
            ORDER BY d.created_at DESC
            """
        ).fetchall()

    documents = []
    for row in rows:
        metadata_raw = row["metadata"] if row["metadata"] else "{}"
        try:
            metadata = json.loads(metadata_raw)
        except (TypeError, json.JSONDecodeError):
            metadata = {}
        preview = (row["text"] or "")
        preview = preview.replace("\n", " ").strip()
        if len(preview) > 120:
            preview = preview[:117] + "..."
        documents.append(
            {
                "id": row["id"],
                "name": row["name"],
                "status": row["status"],
                "size": row["size"],
                "preview": preview,
                "metadata": metadata,
            }
        )
    return documents


@router.delete("/{document_id}", dependencies=[Depends(require_role("admin"))])
def delete_document(document_id: str) -> dict:
    with get_connection() as conn:
        existing = conn.execute("SELECT id FROM documents WHERE id = ?", (document_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
        conn.execute("DELETE FROM document_texts WHERE document_id = ?", (document_id,))
        conn.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        conn.commit()
    return {"message": "Document deleted successfully", "document_id": document_id}
