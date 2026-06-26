import logging
from typing import Any

import numpy as np
from qdrant_client import QdrantClient, models

from app.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "document_chunks"
EMBEDDING_DIM = 384
EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

_client: QdrantClient | None = None
_embedder: Any | None = None


def _get_client() -> QdrantClient | None:
    global _client
    if _client is None:
        try:
            if settings.qdrant_api_key:
                _client = QdrantClient(
                    url=settings.qdrant_url,
                    api_key=settings.qdrant_api_key,
                    timeout=30,
                )
            else:
                _client = QdrantClient(url=settings.qdrant_url, timeout=30)
            _client.get_collections()
            logger.info("Connected to Qdrant at %s", settings.qdrant_url)
        except Exception as e:
            logger.warning("Qdrant connection failed: %s — using fallback mode", e)
            _client = None
    return _client


def _get_embedder():
    global _embedder
    if _embedder is None and _get_client() is not None:
        try:
            from fastembed import TextEmbedding

            _embedder = TextEmbedding(model_name=EMBEDDING_MODEL)
        except Exception as e:
            logger.warning("Embedding model load failed: %s", e)
    return _embedder


def _ensure_collection():
    client = _get_client()
    if client is None:
        return False
    try:
        collections = client.get_collections().collections
        if not any(c.name == COLLECTION_NAME for c in collections):
            client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(
                    size=EMBEDDING_DIM,
                    distance=models.Distance.COSINE,
                ),
            )
            try:
                client.create_payload_index(
                    COLLECTION_NAME, "document_id", models.PayloadSchemaType.KEYWORD
                )
            except Exception:
                pass
            logger.info("Created Qdrant collection: %s", COLLECTION_NAME)
        return True
    except Exception as e:
        logger.warning("Collection setup failed: %s", e)
        return False


def embed_text(text: str) -> list[float] | None:
    embedder = _get_embedder()
    if embedder is None:
        return None
    try:
        vectors = list(embedder.embed([text]))
        if vectors:
            return vectors[0].tolist()
    except Exception as e:
        logger.warning("Embedding failed: %s", e)
    return None


def embed_texts(texts: list[str]) -> list[list[float]] | None:
    embedder = _get_embedder()
    if embedder is None:
        return None
    try:
        return [v.tolist() for v in embedder.embed(texts)]
    except Exception as e:
        logger.warning("Batch embedding failed: %s", e)
    return None


def index_chunks(
    chunks: list[dict[str, Any]],
    document_id: str | None = None,
) -> int:
    client = _get_client()
    if client is None or not _ensure_collection():
        return 0

    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts)
    if vectors is None:
        return 0

    points = []
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        payload: dict[str, Any] = {
            "chunk_id": chunk.get("chunk_id", i),
            "text": chunk["text"],
            "document_id": document_id or chunk.get("document_id", ""),
        }
        if "start" in chunk:
            payload["start"] = chunk["start"]
        if "end" in chunk:
            payload["end"] = chunk["end"]

        points.append(
            models.PointStruct(
                id=hash(f"{document_id or ''}_{chunk.get('chunk_id', i)}") % (2**63),
                vector=vector,
                payload=payload,
            )
        )

    try:
        client.upsert(collection_name=COLLECTION_NAME, points=points)
        logger.info("Indexed %d chunks to Qdrant", len(points))
        return len(points)
    except Exception as e:
        logger.warning("Qdrant upsert failed: %s", e)
        return 0


def search_chunks(
    query: str,
    limit: int = 10,
    score_threshold: float | None = None,
) -> list[dict[str, Any]]:
    client = _get_client()
    if client is None or not _ensure_collection():
        return []

    query_vector = embed_text(query)
    if query_vector is None:
        return []

    try:
        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=limit,
            score_threshold=score_threshold,
        )
        return [
            {
                "text": r.payload.get("text", ""),
                "score": r.score,
                "document_id": r.payload.get("document_id", ""),
                "chunk_id": r.payload.get("chunk_id"),
            }
            for r in results.points
        ]
    except Exception as e:
        logger.warning("Qdrant search failed: %s", e)
        return []


def hybrid_search(
    query: str,
    text_results: list[dict[str, Any]],
    vector_weight: float = 0.6,
    text_weight: float = 0.4,
    limit: int = 10,
) -> list[dict[str, Any]]:
    vector_results = search_chunks(query, limit=limit * 2)

    if not vector_results:
        return text_results[:limit]

    combined: dict[str, dict[str, Any]] = {}
    for r in text_results:
        doc_id = r.get("document_id", r.get("document_name", ""))
        combined[doc_id] = {
            "document_id": doc_id,
            "text": r.get("text", ""),
            "text_score": r.get("score", 0) * text_weight,
            "vector_score": 0,
            "matched_entities": r.get("matched_entities", []),
            "document_name": r.get("document_name", ""),
        }

    for r in vector_results:
        doc_id = r.get("document_id", "")
        if doc_id in combined:
            combined[doc_id]["vector_score"] = max(
                combined[doc_id]["vector_score"], r["score"] * vector_weight
            )
        else:
            combined[doc_id] = {
                "document_id": doc_id,
                "text": r.get("text", ""),
                "text_score": 0,
                "vector_score": r["score"] * vector_weight,
                "matched_entities": [],
                "document_name": "",
            }

    for item in combined.values():
        item["score"] = item["text_score"] + item["vector_score"]

    sorted_results = sorted(combined.values(), key=lambda x: x["score"], reverse=True)
    return sorted_results[:limit]


def delete_document_vectors(document_id: str) -> bool:
    client = _get_client()
    if client is None:
        return False
    try:
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=models.Filter(
                must=[
                    models.FieldCondition(
                        key="document_id",
                        match=models.MatchValue(value=document_id),
                    )
                ]
            ),
        )
        return True
    except Exception as e:
        logger.warning("Qdrant delete failed: %s", e)
        return False


def get_collection_stats() -> dict:
    client = _get_client()
    if client is None:
        return {"status": "disconnected", "points_count": 0}
    try:
        info = client.get_collection(COLLECTION_NAME)
        return {
            "status": "connected",
            "points_count": info.points_count,
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "points_count": 0}
