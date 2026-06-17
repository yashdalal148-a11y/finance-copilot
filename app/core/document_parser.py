"""
Document Parser Helper.

Extracts plain text from uploaded files (PDF, DOCX) to be passed into
the LLM for intelligence extraction.
"""

from __future__ import annotations

import io
import logging

logger = logging.getLogger(__name__)


def extract_text_from_file(file_bytes: bytes, file_name: str) -> str:
    """Extract plain text from a file based on its extension."""
    ext = file_name.split(".")[-1].lower()
    
    if ext == "pdf":
        return _extract_from_pdf(file_bytes)
    elif ext in ["doc", "docx"]:
        return _extract_from_docx(file_bytes)
    elif ext in ["txt", "md"]:
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        logger.warning("Unsupported file type: %s. Attempting to read as plain text.", ext)
        return file_bytes.decode("utf-8", errors="ignore")


def _extract_from_pdf(file_bytes: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        logger.error("pypdf is not installed. Cannot parse PDF.")
        return "ERROR: pypdf not installed."

    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
        return "\n".join(text)
    except Exception as exc:
        logger.error("Failed to parse PDF: %s", exc, exc_info=True)
        return f"ERROR: Failed to parse PDF ({exc})"


def _extract_from_docx(file_bytes: bytes) -> str:
    try:
        import docx
    except ImportError:
        logger.error("python-docx is not installed. Cannot parse DOCX.")
        return "ERROR: python-docx not installed."

    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join([p.text for p in doc.paragraphs])
    except Exception as exc:
        logger.error("Failed to parse DOCX: %s", exc, exc_info=True)
        return f"ERROR: Failed to parse DOCX ({exc})"
