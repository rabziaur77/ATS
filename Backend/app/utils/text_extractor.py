"""
Module: text_extractor.py
Created: 2026-09-03
Purpose: Low-level text extraction from raw file bytes (PDF, DOCX, TXT).
"""

import io
from typing import Union

import pdfplumber
from docx import Document

from app.utils.exceptions import UnsupportedFileType

TextSource = Union[bytes, bytearray, memoryview]


def extract_text_bytes(data: TextSource, file_type: str) -> str:
    """Extract plain text from a CV file's raw bytes.

    Args:
        data: Raw file content as bytes.
        file_type: Lowercase extension without dot: pdf, docx, or txt.

    Returns:
        str: The plain text content of the file.

    Raises:
        UnsupportedFileType: If file_type is not pdf/docx/txt.
        ValueError: If extraction fails for a supported type.
    """
    file_type = file_type.lower().lstrip(".")
    if file_type == "pdf":
        return _from_pdf(data)
    if file_type == "docx":
        return _from_docx(data)
    if file_type == "txt":
        return _from_txt(data)
    raise UnsupportedFileType(file_type)


def _from_pdf(data: TextSource) -> str:
    """Extract text from a PDF byte stream using pdfplumber.

    Args:
        data: Raw PDF bytes.

    Returns:
        str: Concatenated text from all PDF pages.

    Raises:
        ValueError: If the PDF cannot be read.
    """
    try:
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        return "\n\n".join(pages).strip()
    except Exception as exc:  # pdfplumber raises varied errors
        raise ValueError(f"Failed to extract text from PDF: {exc}") from exc


def _from_docx(data: TextSource) -> str:
    """Extract text from a DOCX byte stream using python-docx.

    Args:
        data: Raw DOCX bytes.

    Returns:
        str: Paragraph text joined by newlines.

    Raises:
        ValueError: If the DOCX cannot be read.
    """
    try:
        doc = Document(io.BytesIO(data))
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception as exc:
        raise ValueError(f"Failed to extract text from DOCX: {exc}") from exc


def _from_txt(data: TextSource) -> str:
    """Decode plain text bytes, tolerating common encodings.

    Args:
        data: Raw text bytes.

    Returns:
        str: The decoded text, stripped of surrounding whitespace.
    """
    raw = bytes(data)
    for encoding in ("utf-8", "latin-1"):
        try:
            return raw.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="ignore").strip()
