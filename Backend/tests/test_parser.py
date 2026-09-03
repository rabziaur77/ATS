"""
Module: test_parser.py
Created: 2026-09-03
Purpose: Unit tests for CV text extraction and restructuring.
"""

from pathlib import Path

from app.services.cv_parser import parse_cv
from app.utils.exceptions import UnsupportedFileType
from app.utils.text_extractor import extract_text_bytes

FIXTURES = Path(__file__).parent / "fixtures"


def _read(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def test_extract_txt():
    text = extract_text_bytes(_read("sample_cv.txt"), "txt")
    assert "John Doe" in text


def test_extract_unsupported():
    try:
        extract_text_bytes(b"data", "png")
        assert False, "should raise"
    except UnsupportedFileType:
        pass


def test_parse_txt_structure():
    data = parse_cv(_read("sample_cv.txt"), "txt")
    assert data.personal_info.name == "John Doe"
    assert data.personal_info.email == "john.doe@example.com"
    assert "Python" in data.skills
    assert len(data.experience) >= 2
    assert len(data.education) >= 1
