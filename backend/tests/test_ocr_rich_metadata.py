import io

from app.services.ocr import extract_text_and_metadata, OCRResult


def test_extract_text_and_metadata_returns_rich_metadata() -> None:
    content = b"Pump Inspection Report\nEquipment: Pump A\nStatus: Healthy\nNext Action: Maintenance"
    result = extract_text_and_metadata("report.txt", content)

    assert result.text
    assert result.metadata["character_count"] > 0
    assert result.metadata["line_count"] == 4
    assert result.metadata["section_count"] >= 1
    assert "Pump" in result.metadata["keywords"]


def test_extract_txt_multiline() -> None:
    content = b"Line one\nLine two\nLine three\nLine four\nLine five"
    result = extract_text_and_metadata("multi.txt", content)
    assert result.metadata["line_count"] == 5
    assert result.text == "Line one\nLine two\nLine three\nLine four\nLine five"


def test_extract_txt_with_sections() -> None:
    content = b"Introduction:\nThis is the intro.\nMethod:\nThis is the method.\nConclusion:\nThis is the conclusion."
    result = extract_text_and_metadata("sections.txt", content)
    assert result.metadata["section_count"] >= 3


def test_extract_txt_keywords_filtered() -> None:
    content = b"pump motor valve bearing seal compressor turbine heat exchanger"
    result = extract_text_and_metadata("keywords.txt", content)
    assert len(result.metadata["keywords"]) > 0
    assert all(len(kw) > 3 for kw in result.metadata["keywords"])


def test_extract_pdf_with_blank_page() -> None:
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
    result = extract_text_and_metadata("blank.pdf", min_pdf)
    assert isinstance(result, OCRResult)
    assert result.metadata["page_count"] == 1
    assert result.metadata["file_type"] == "pdf"
    assert result.metadata["character_count"] >= 0


def test_extract_csv_with_data() -> None:
    content = b"equipment,status,date\npump,good,2024-01-01\nmotor,fair,2024-01-02\nvalve,good,2024-01-03"
    result = extract_text_and_metadata("data.csv", content)
    assert isinstance(result, OCRResult)
    assert result.text
    assert "pump" in result.text.lower()
    assert result.metadata["file_type"] == "csv"


def test_extract_pdf_corrupt_returns_error() -> None:
    result = extract_text_and_metadata("bad.pdf", b"garbage not a pdf")
    assert isinstance(result, OCRResult)
    assert "extraction_error" in result.metadata
    assert result.text == ""


def test_extract_docx_corrupt_returns_error() -> None:
    result = extract_text_and_metadata("bad.docx", b"garbage not a docx")
    assert isinstance(result, OCRResult)
    assert "extraction_error" in result.metadata
    assert result.text == ""


def test_extract_unsupported_type_raises() -> None:
    try:
        extract_text_and_metadata("file.xyz", b"some content")
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "Unsupported file type" in str(e)


def test_metadata_fields_present() -> None:
    content = b"Test content with some words for metadata validation."
    result = extract_text_and_metadata("test.txt", content)
    for key in ("filename", "file_type", "character_count", "char_count", "word_count", "estimated_page_count"):
        assert key in result.metadata, f"Missing metadata field: {key}"
    assert result.metadata["filename"] == "test.txt"
    assert result.metadata["file_type"] == "txt"
    assert result.metadata["word_count"] > 0
    assert result.metadata["estimated_page_count"] >= 1
