"""Tests for the RAG pipeline: chunker and pdf_processor."""
from unittest.mock import patch, MagicMock


# ---------- chunk_text ----------

def test_chunk_text_short_returns_single():
    """Short text shorter than chunk_size returns a single chunk."""
    from rag.chunker import chunk_text
    text = "This is a short piece of text."
    chunks = chunk_text(text, chunk_size=1000, chunk_overlap=200)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunk_text_empty_returns_empty():
    """Empty or whitespace-only text returns no chunks."""
    from rag.chunker import chunk_text
    assert chunk_text("", chunk_size=100) == []
    assert chunk_text("   \n\n  ", chunk_size=100) == []


def test_chunk_text_long_splits():
    """Text longer than chunk_size produces multiple chunks."""
    from rag.chunker import chunk_text
    # Create text that's clearly > 1000 chars with paragraph breaks
    paragraphs = ["Paragraph number {i}. " * 20 for i in range(10)]
    text = "\n\n".join(paragraphs)
    chunks = chunk_text(text, chunk_size=500, chunk_overlap=100)
    assert len(chunks) > 1
    # All chunks should be non-empty
    for c in chunks:
        assert len(c.strip()) > 0


# ---------- chunk_document ----------

def test_chunk_document_metadata():
    """chunk_document produces chunks with correct metadata."""
    from rag.chunker import chunk_document
    pages = [
        {"page_number": 1, "text": "Content from page one about academics."},
        {"page_number": 2, "text": "Content from page two about schedules."},
    ]
    chunks = chunk_document(pages, "test_doc.pdf", chunk_size=1000, chunk_overlap=200)
    assert len(chunks) >= 2
    for chunk in chunks:
        assert "text" in chunk
        assert "metadata" in chunk
        meta = chunk["metadata"]
        assert meta["source"] == "test_doc.pdf"
        assert "page" in meta
        assert "chunk_index" in meta


def test_chunk_document_preserves_page_numbers():
    """Each chunk's metadata references the correct page number."""
    from rag.chunker import chunk_document
    pages = [
        {"page_number": 3, "text": "Page three content."},
        {"page_number": 7, "text": "Page seven content."},
    ]
    chunks = chunk_document(pages, "doc.pdf")
    page_nums = [c["metadata"]["page"] for c in chunks]
    assert 3 in page_nums
    assert 7 in page_nums


# ---------- extract_text_from_pdf ----------

def test_extract_text_from_pdf():
    """extract_text_from_pdf extracts text page-by-page."""
    mock_page1 = MagicMock()
    mock_page1.get_text.return_value = "Page 1 text content"

    mock_page2 = MagicMock()
    mock_page2.get_text.return_value = "Page 2 text content"

    mock_doc = MagicMock()
    mock_doc.__enter__ = MagicMock(return_value=mock_doc)
    mock_doc.__exit__ = MagicMock(return_value=False)
    mock_doc.__len__ = MagicMock(return_value=2)
    mock_doc.__getitem__ = lambda self, idx: [mock_page1, mock_page2][idx]

    with patch("rag.pdf_processor.pymupdf") as mock_pymupdf:
        mock_pymupdf.open.return_value = mock_doc
        from rag.pdf_processor import extract_text_from_pdf
        result = extract_text_from_pdf("test.pdf")

    assert len(result) == 2
    assert result[0]["page_number"] == 1
    assert result[0]["text"] == "Page 1 text content"
    assert result[1]["page_number"] == 2
    assert result[1]["text"] == "Page 2 text content"


def test_extract_text_from_pdf_skips_empty_pages():
    """Pages with no text (and no OCR) are skipped."""
    mock_page = MagicMock()
    mock_page.get_text.return_value = ""  # empty page

    mock_doc = MagicMock()
    mock_doc.__enter__ = MagicMock(return_value=mock_doc)
    mock_doc.__exit__ = MagicMock(return_value=False)
    mock_doc.__len__ = MagicMock(return_value=1)
    mock_doc.__getitem__ = lambda self, idx: mock_page

    with patch("rag.pdf_processor.pymupdf") as mock_pymupdf, \
         patch("rag.pdf_processor._ocr_available", False):
        mock_pymupdf.open.return_value = mock_doc
        from rag.pdf_processor import extract_text_from_pdf
        result = extract_text_from_pdf("empty.pdf")

    assert len(result) == 0
