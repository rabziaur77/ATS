"""
Module: cv_parser.py
Created: 2026-09-03
Purpose: Parses uploaded CV files into structured JSON via text extraction
         and content restructuring.
"""

from app.schemas.resume import ParsedResumeData
from app.utils.content_restructurer import restructure
from app.utils.text_extractor import extract_text_bytes


def parse_cv(data: bytes, file_type: str) -> ParsedResumeData:
    """Parse raw CV bytes into structured resume data.

    Args:
        data: Raw CV file content.
        file_type: pdf, docx, or txt (case-insensitive).

    Returns:
        ParsedResumeData: Structured CV content.
    """
    raw_text = extract_text_bytes(data, file_type)
    return restructure(raw_text)
