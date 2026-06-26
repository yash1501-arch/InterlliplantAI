import json
import io

from app.services.ocr import extract_text_and_metadata, OCRResult
from app.services.chunking import chunk_text
from app.services.entities import extract_entities
from app.services.relationships import extract_relationships
from app.services.retrieval import build_demo_search_result


def test_ocr_with_empty_txt() -> None:
    result = extract_text_and_metadata("empty.txt", b"")
    assert isinstance(result, OCRResult)
    assert result.text == ""
    assert result.metadata["character_count"] == 0


def test_ocr_with_empty_pdf() -> None:
    min_pdf = (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R>>endobj\n"
        b"xref\n0 4\n"
        b"0000000000 65535 f \n"
        b"0000000009 00000 n \n"
        b"0000000058 00000 n \n"
        b"0000000115 00000 n \n"
        b"trailer<</Size 4/Root 1 0 R>>\n"
        b"startxref\n190\n%%EOF"
    )
    result = extract_text_and_metadata("empty.pdf", min_pdf)
    assert isinstance(result, OCRResult)
    assert result.metadata["page_count"] == 1


def test_ocr_with_corrupt_pdf() -> None:
    result = extract_text_and_metadata("corrupt.pdf", b"this is not a valid pdf")
    assert isinstance(result, OCRResult)
    assert result.text == ""
    assert result.metadata.get("extraction_error") is not None


def test_ocr_with_corrupt_docx() -> None:
    result = extract_text_and_metadata("corrupt.docx", b"not a docx file")
    assert isinstance(result, OCRResult)
    assert result.text == ""
    assert result.metadata.get("extraction_error") is not None


def test_ocr_with_unicode_text() -> None:
    content = "Moteur à haute température: vérifier l'alignement".encode("utf-8")
    result = extract_text_and_metadata("unicode.txt", content)
    assert isinstance(result, OCRResult)
    assert result.text
    assert "température" in result.text or "temperature" in result.text.lower()


def test_ocr_with_binary_bytes_txt() -> None:
    content = b"\x00\x01\x02\xff\xfe\xfd"
    result = extract_text_and_metadata("binary.txt", content)
    assert isinstance(result, OCRResult)
    assert result.metadata["character_count"] >= 0


def test_chunk_text_empty_string() -> None:
    result = chunk_text("")
    assert result == []


def test_chunk_text_smaller_than_chunk_size() -> None:
    text = "Hello world, this is a short text."
    result = chunk_text(text, chunk_size=1024)
    assert len(result) == 1
    assert result[0]["text"] == text
    assert result[0]["chunk_id"] == 0


def test_chunk_text_exact_chunk_size() -> None:
    text = "a" * 1024
    result = chunk_text(text, chunk_size=1024)
    assert len(result) == 1
    assert len(result[0]["text"]) == 1024


def test_chunk_text_larger_than_chunk_size() -> None:
    text = "a" * 3000
    result = chunk_text(text, chunk_size=1024, overlap=200)
    assert len(result) > 1
    for chunk in result:
        assert len(chunk["text"]) <= 1024


def test_chunk_text_with_overlap() -> None:
    text = "The quick brown fox jumps over the lazy dog. " * 50
    result = chunk_text(text, chunk_size=100, overlap=20)
    assert len(result) >= 2
    if len(result) >= 2:
        overlap_text = result[0]["text"][-20:]
        assert overlap_text in result[1]["text"]


def test_chunk_text_non_ascii() -> None:
    text = "café résumé über cool " * 100
    result = chunk_text(text, chunk_size=200, overlap=30)
    assert len(result) >= 1
    assert all(c["text"] for c in result)


def test_extract_entities_empty_text() -> None:
    result = extract_entities("")
    assert result == []


def test_extract_entities_no_match() -> None:
    result = extract_entities("The quick brown fox jumps over the lazy dog.")
    assert result == []


def test_extract_entities_equipment_only() -> None:
    result = extract_entities("The pump is running and the motor is过热.")
    types = {e["type"] for e in result}
    assert "EQUIPMENT" in types
    assert any("pump" in e["entity"].lower() for e in result)


def test_extract_entities_all_types() -> None:
    text = (
        "The pump experienced a bearing failure leading to a fire. "
        "The operator reported the incident. OISD standards require inspection. "
        "The engineer should review ISO 9001 compliance."
    )
    result = extract_entities(text)
    types_found = {e["type"] for e in result}
    for expected in ("EQUIPMENT", "FAILURE", "INCIDENT", "REGULATION", "PERSONNEL"):
        assert expected in types_found, f"Missing entity type: {expected}"


def test_extract_entities_with_context() -> None:
    text = "The centrifugal pump failed due to cavitation issues."
    result = extract_entities(text)
    assert len(result) >= 2
    for entity in result:
        assert "entity" in entity
        assert "type" in entity
        assert "confidence" in entity
        assert "context" in entity


def test_extract_relationships_no_entities() -> None:
    result = extract_relationships([], "Some text about nothing in particular.")
    assert result == []


def test_extract_relationships_single_entity() -> None:
    entities = [{"entity": "pump", "type": "EQUIPMENT", "confidence": 1.0}]
    result = extract_relationships(entities, "The pump failed.")
    assert result == []


def test_extract_relationships_two_entities_no_trigger() -> None:
    entities = [
        {"entity": "pump", "type": "EQUIPMENT", "confidence": 1.0},
        {"entity": "motor", "type": "EQUIPMENT", "confidence": 1.0},
    ]
    text = "The pump is here and the motor is over there."
    result = extract_relationships(entities, text)
    assert isinstance(result, list)
    for rel in result:
        assert "source" in rel
        assert "target" in rel
        assert "type" in rel


def test_build_demo_search_result_no_documents() -> None:
    result = build_demo_search_result("pump failure", documents=[])
    assert result["query"] == "pump failure"
    assert result["results"] == []


def test_build_demo_search_result_empty_query_with_docs() -> None:
    docs = [
        {
            "document_id": "1",
            "text": "Pump inspection checklist",
            "document_name": "pump.txt",
            "metadata": {},
        }
    ]
    result = build_demo_search_result("", documents=docs)
    assert result["query"] == ""
    assert result["results"] == []


def test_build_demo_search_result_short_query_terms() -> None:
    docs = [
        {
            "document_id": "1",
            "text": "Pump inspection checklist for maintenance",
            "document_name": "pump.txt",
            "metadata": {},
        }
    ]
    result = build_demo_search_result("a an of", documents=docs)
    assert result["results"] == []


def test_build_demo_search_result_single_doc_match() -> None:
    docs = [
        {
            "document_id": "d1",
            "text": "Pump inspection and vibration analysis",
            "document_name": "pump_report.txt",
            "metadata": {},
        }
    ]
    result = build_demo_search_result("pump vibration", documents=docs)
    assert len(result["results"]) == 1
    assert result["results"][0]["score"] > 0


def test_build_demo_search_result_multiple_docs_ranking() -> None:
    docs = [
        {
            "document_id": "d1",
            "text": "Pump inspection checklist for vibration analysis",
            "document_name": "pump_doc.txt",
            "metadata": {},
        },
        {
            "document_id": "d2",
            "text": "Weather report for the city today",
            "document_name": "weather.txt",
            "metadata": {},
        },
    ]
    result = build_demo_search_result("pump vibration", documents=docs)
    assert len(result["results"]) == 2
    assert result["results"][0]["score"] >= result["results"][1]["score"]


def test_build_demo_search_result_matched_entities() -> None:
    docs = [
        {
            "document_id": "d1",
            "text": "The pump experienced a failure during operation",
            "document_name": "failure_report.txt",
            "metadata": {},
        }
    ]
    result = build_demo_search_result("pump failure", documents=docs)
    assert len(result["results"]) == 1
    assert "matched_entities" in result["results"][0]


def test_build_demo_search_result_with_metadata() -> None:
    docs = [
        {
            "document_id": "d1",
            "text": "Pump maintenance procedure",
            "document_name": "sop_pump.txt",
            "metadata": {"source": "manual", "version": "2.0"},
        }
    ]
    result = build_demo_search_result("pump", documents=docs)
    assert len(result["results"]) == 1
    assert result["results"][0]["document_name"] == "sop_pump.txt"
