"""PDF text extraction module.

Supports both text-based and image-based (scanned) PDFs.
For image-based PDFs, uses OCR via pytesseract if Tesseract is installed,
otherwise logs a warning and skips those pages.
"""
import io
import logging

import pymupdf

logger = logging.getLogger(__name__)

# Check if OCR is available
_ocr_available = False
try:
    import pytesseract
    from PIL import Image
    # Quick check that tesseract binary is accessible
    pytesseract.get_tesseract_version()
    _ocr_available = True
    logger.info("Tesseract OCR is available for image-based PDFs.")
except Exception:
    logger.warning(
        "Tesseract OCR is not available. Image-based PDF pages will be skipped. "
        "Install Tesseract to enable OCR: https://github.com/tesseract-ocr/tesseract"
    )


def _ocr_page(page) -> str:
    """Render a PDF page as an image and run OCR on it."""
    if not _ocr_available:
        return ""
    try:
        pix = page.get_pixmap(dpi=300)
        img_data = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_data))
        text = pytesseract.image_to_string(img, lang="eng")
        return text.strip()
    except Exception as e:
        logger.warning(f"OCR failed for page: {e}")
        return ""


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """Extract text from a PDF file, page by page.

    For each page, first attempts direct text extraction.
    If the page contains no text (e.g., scanned image), falls back to OCR.

    Args:
        file_path: Path to the PDF file.

    Returns:
        List of dicts with 'page_number' (1-indexed) and 'text' keys.
    """
    pages_text = []
    try:
        with pymupdf.open(file_path) as doc:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text().strip()

                if not text:
                    # Try OCR for image-based pages
                    logger.info(
                        f"No text on page {page_num + 1} of {file_path}, attempting OCR..."
                    )
                    text = _ocr_page(page)
                    if text:
                        logger.info(
                            f"OCR extracted {len(text)} chars from page {page_num + 1}"
                        )
                    else:
                        logger.warning(
                            f"No text could be extracted from page {page_num + 1} of {file_path}"
                        )

                if text:
                    pages_text.append({
                        "page_number": page_num + 1,
                        "text": text,
                    })
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        raise
    return pages_text
