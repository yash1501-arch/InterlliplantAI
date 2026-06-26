import json
import logging
import math
from typing import Any

from app.db.database import get_connection
from app.services.entities import extract_entities

logger = logging.getLogger(__name__)


def _load_documents(filters: dict | None = None) -> list[dict]:
    with get_connection() as conn:
        query = """
            SELECT d.id, d.filename, dt.text, dt.metadata,
                   d.status, d.created_at, d.content_type
            FROM documents d
            LEFT JOIN document_texts dt ON dt.document_id = d.id
            WHERE 1=1
        """
        params: list[Any] = []
        if filters:
            if filters.get("file_type"):
                query += " AND d.content_type LIKE ?"
                params.append(f"%{filters['file_type']}%")
            if filters.get("date_from"):
                query += " AND d.created_at >= ?"
                params.append(filters["date_from"])
            if filters.get("date_to"):
                query += " AND d.created_at <= ?"
                params.append(filters["date_to"])
            if filters.get("status"):
                query += " AND d.status = ?"
                params.append(filters["status"])
        rows = conn.execute(query, params).fetchall()

    documents = []
    for row in rows:
        try:
            meta = json.loads(row["metadata"] or "{}")
        except (json.JSONDecodeError, TypeError):
            meta = {}
        documents.append({
            "document_id": row["id"],
            "text": row["text"] or "",
            "document_name": row["filename"] or "Extracted document",
            "metadata": meta,
        })
    return documents


def _bm25_score(query: str, documents: list[dict]) -> list[dict]:
    """BM25-style scoring against document texts."""
    if not documents:
        return []

    lowered_query = query.lower()
    query_terms = [t for t in lowered_query.split() if len(t) > 2]

    if not query_terms:
        return []

    total_docs = len(documents)
    avg_dl = sum(len(doc["text"].split()) for doc in documents) / max(total_docs, 1)
    k1 = 1.5
    b = 0.75

    # IDF
    idf = {}
    for term in query_terms:
        docs_with_term = sum(1 for doc in documents if term in doc["text"].lower())
        idf[term] = math.log((total_docs - docs_with_term + 0.5) / (docs_with_term + 0.5) + 1)

    results = []
    for doc in documents:
        doc_text_lower = doc["text"].lower()
        doc_words = doc_text_lower.split()
        dl = len(doc_words)

        score = 0.0
        for term in query_terms:
            tf = doc_text_lower.count(term)
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * dl / avg_dl)
            score += idf.get(term, 0) * (numerator / denominator)

        if score > 0:
            # Entity matching bonus
            doc_entities = [e["entity"].lower() for e in extract_entities(doc["text"])]
            entity_matches = [
                e for e in doc_entities
                if any(t in e or e in t for t in query_terms)
            ]

            snippet = doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"]
            results.append({
                "document_id": doc["document_id"],
                "text": snippet,
                "score": score,
                "matched_entities": entity_matches,
                "document_name": doc["document_name"],
            })

    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def _graph_search(query: str) -> list[dict]:
    """Graph-based search via Neo4j or local entity/relationship matching."""
    try:
        from app.services.neo4j_service import is_connected, _run_query as neo4j_query
        from app.services.entities import extract_entities as extract_ents

        query_entities = extract_ents(query)
        results = []

        if is_connected():
            for ent in query_entities[:3]:
                node_id = ent["entity"].lower().replace(" ", "_")
                related = neo4j_query(
                    """
                    MATCH (n)-[r]-(connected)
                    WHERE n.id CONTAINS $query OR n.name CONTAINS $name
                    OPTIONAL MATCH (connected)-[:DESCRIBED_BY]->(d:Document)
                    RETURN connected.name AS name, labels(connected) AS types,
                           type(r) AS rel_type, d.id AS doc_id, d.name AS doc_name
                    LIMIT 10
                    """,
                    {"query": node_id[:50], "name": ent["entity"]},
                )
                for row in related:
                    if row.get("doc_id"):
                        results.append({
                            "document_id": row["doc_id"],
                            "text": f"{ent['entity']} --[{row.get('rel_type', '?')}]--> {row.get('name', '?')}",
                            "score": 0.8,
                            "matched_entities": [ent["entity"], row.get("name", "")],
                            "document_name": row.get("doc_name", ""),
                            "graph_relation": row.get("rel_type", ""),
                        })

        # Fallback: local entity-based graph traversal
        if not results:
            with get_connection() as conn:
                for ent in query_entities[:3]:
                    rows = conn.execute(
                        """
                        SELECT d.id, d.filename, dt.text
                        FROM documents d
                        JOIN document_texts dt ON dt.document_id = d.id
                        WHERE LOWER(dt.text) LIKE ?
                        LIMIT 5
                        """,
                        (f"%{ent['entity'].lower()}%",),
                    ).fetchall()
                    for row in rows:
                        snippet = row["text"][:200] if row["text"] else ""
                        results.append({
                            "document_id": row["id"],
                            "text": snippet,
                            "score": 0.7,
                            "matched_entities": [ent["entity"]],
                            "document_name": row["filename"],
                            "graph_relation": "CONTAINS_ENTITY",
                        })

        return results
    except Exception as e:
        logger.warning("Graph search failed: %s", e)
        return []


def _vector_search(query: str, limit: int = 10) -> list[dict]:
    """Semantic vector search via Qdrant."""
    try:
        from app.services.vector_store import search_chunks
        results = search_chunks(query, limit=limit)
        return [
            {
                "document_id": r.get("document_id", ""),
                "text": r.get("text", ""),
                "score": r.get("score", 0),
                "matched_entities": [],
                "document_name": "",
            }
            for r in results
        ]
    except Exception as e:
        logger.warning("Vector search failed: %s", e)
        return []


def hybrid_retrieval(
    query: str,
    documents: list[dict] | None = None,
    vector_weight: float = 0.4,
    graph_weight: float = 0.4,
    bm25_weight: float = 0.2,
    limit: int = 10,
) -> list[dict]:
    """
    Full hybrid search: 40% Vector + 40% Graph + 20% BM25
    As specified in the architecture documents.
    """
    if documents is None:
        documents = _load_documents()

    # Run all three search legs
    bm25_results = _bm25_score(query, documents)
    vector_results = _vector_search(query, limit=limit * 2)
    graph_results = _graph_search(query)

    # Normalize scores within each result set
    def normalize(results: list[dict]) -> list[dict]:
        if not results:
            return []
        max_score = max(r["score"] for r in results)
        if max_score > 0:
            for r in results:
                r["normalized_score"] = r["score"] / max_score
        else:
            for r in results:
                r["normalized_score"] = 0
        return results

    bm25_results = normalize(bm25_results)
    vector_results = normalize(vector_results)
    graph_results = normalize(graph_results)

    # Merge by document_id using weighted scoring
    combined: dict[str, dict] = {}

    for r in bm25_results:
        doc_id = r["document_id"]
        if doc_id not in combined:
            combined[doc_id] = {
                "document_id": doc_id,
                "text": r["text"],
                "bm25_score": 0,
                "vector_score": 0,
                "graph_score": 0,
                "matched_entities": [],
                "document_name": r.get("document_name", ""),
            }
        combined[doc_id]["bm25_score"] = max(combined[doc_id]["bm25_score"], r["normalized_score"])
        combined[doc_id]["matched_entities"] = list(set(combined[doc_id]["matched_entities"] + r.get("matched_entities", [])))

    for r in vector_results:
        doc_id = r["document_id"]
        if doc_id not in combined:
            combined[doc_id] = {
                "document_id": doc_id,
                "text": r["text"],
                "bm25_score": 0,
                "vector_score": 0,
                "graph_score": 0,
                "matched_entities": [],
                "document_name": r.get("document_name", ""),
            }
        combined[doc_id]["vector_score"] = max(combined[doc_id]["vector_score"], r["normalized_score"])

    for r in graph_results:
        doc_id = r["document_id"]
        if doc_id not in combined:
            combined[doc_id] = {
                "document_id": doc_id,
                "text": r["text"],
                "bm25_score": 0,
                "vector_score": 0,
                "graph_score": 0,
                "matched_entities": [],
                "document_name": r.get("document_name", ""),
            }
        combined[doc_id]["graph_score"] = max(combined[doc_id]["graph_score"], r["normalized_score"])
        combined[doc_id]["matched_entities"] = list(set(combined[doc_id]["matched_entities"] + r.get("matched_entities", [])))

    # Apply weighted formula: 40% vector + 40% graph + 20% BM25
    for item in combined.values():
        item["score"] = (
            vector_weight * item["vector_score"]
            + graph_weight * item["graph_score"]
            + bm25_weight * item["bm25_score"]
        )

    sorted_results = sorted(combined.values(), key=lambda x: x["score"], reverse=True)
    return sorted_results[:limit]


def build_demo_search_result(
    query: str, documents: list[dict] | None = None
) -> dict:
    """Primary search function using full hybrid retrieval."""
    if documents is None:
        documents = _load_documents()

    if not documents:
        return {"query": query, "results": []}

    hybrid_results = hybrid_retrieval(query, documents, limit=10)

    results = [
        {
            "id": r["document_id"],
            "title": r.get("document_name", ""),
            "snippet": r.get("text", "")[:200],
            "score": r["score"],
            "matched_entities": r.get("matched_entities", []),
            "document_name": r.get("document_name", ""),
            "retrieval_scores": {
                "vector": round(r.get("vector_score", 0), 3),
                "graph": round(r.get("graph_score", 0), 3),
                "bm25": round(r.get("bm25_score", 0), 3),
            },
        }
        for r in hybrid_results
    ]

    return {"query": query, "results": results}


def search_with_pagination(
    query: str,
    page: int = 1,
    page_size: int = 20,
    filters: dict | None = None,
) -> dict:
    documents = _load_documents(filters)

    if not documents:
        return {
            "query": query,
            "results": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
        }

    hybrid_results = hybrid_retrieval(query, documents, limit=100)
    total = len(hybrid_results)
    total_pages = max(1, (total + page_size - 1) // page_size)

    start = (page - 1) * page_size
    end = start + page_size
    page_results = [
        {
            "id": r["document_id"],
            "title": r.get("document_name", ""),
            "snippet": r.get("text", "")[:200],
            "score": r["score"],
            "matched_entities": r.get("matched_entities", []),
            "document_name": r.get("document_name", ""),
            "retrieval_scores": {
                "vector": round(r.get("vector_score", 0), 3),
                "graph": round(r.get("graph_score", 0), 3),
                "bm25": round(r.get("bm25_score", 0), 3),
            },
        }
        for r in hybrid_results[start:end]
    ]

    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO recent_searches (query, page, page_size, result_count) VALUES (?, ?, ?, ?)",
                (query, page, page_size, total),
            )
            conn.commit()
    except Exception:
        pass

    return {
        "query": query,
        "results": page_results,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
