from typing import Any


def chunk_text(text: str, chunk_size: int = 1024, overlap: int = 200) -> list[dict[str, Any]]:
    if not text:
        return []

    if len(text) <= chunk_size:
        return [{"chunk_id": 0, "text": text, "start": 0, "end": len(text)}]

    chunks: list[dict[str, Any]] = []
    start = 0
    chunk_id = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append({
            "chunk_id": chunk_id,
            "text": text[start:end],
            "start": start,
            "end": end,
        })
        chunk_id += 1
        if end >= len(text):
            break
        start = end - overlap

    return chunks
