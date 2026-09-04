"""
Module: text_extractor.py
Created: 2026-09-03
Purpose: Low-level text extraction from raw file bytes (PDF, DOCX, TXT).
"""

import io
from collections import defaultdict
from typing import Optional, Union

import pdfplumber
from docx import Document

from app.utils.exceptions import UnsupportedFileType

TextSource = Union[bytes, bytearray, memoryview]

# Minimum horizontal separation (PDF units) between a column's right edge and
# the next column's left edge for the page to count as two-column.
COLUMN_GAP_PX = 12.0
# Minimum number of words a column cluster needs to qualify as a real column
# (guards against right-aligned date runs or stray words posing as a column).
MIN_COLUMN_WORDS = 8
# Inter-word gap above which two words are treated as separate inline "chips"
# (e.g. skill badges rendered with padding) and joined with a comma.
CHIP_GAP_PX = 7.0
# Upper bound for chip-comma joining. Wider gaps are flex-aligned spans (e.g.
# a title and its right-aligned dates) that must stay single-spaced.
CHIP_COMMA_MAX_PX = 40.0


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
            pages = [_page_to_text(page) for page in pdf.pages]
        return "\n\n".join(pages).strip()
    except Exception as exc:  # pdfplumber raises varied errors
        raise ValueError(f"Failed to extract text from PDF: {exc}") from exc


def _page_to_text(page) -> str:
    """Extract a single PDF page as text, handling multi-column layouts.

    Two-column templates (e.g. the modern sidebar layout) place the skills
    column at a distinctly smaller ``x0`` than the main column. A naive
    row-by-row ``extract_text()`` interleaves the two columns, scrambling the
    resume. This helper detects the columns from word positions and emits the
    left column top-to-bottom followed by the right column, so each section
    keeps its own coherent text run.

    Args:
        page: A pdfplumber Page object.

    Returns:
        str: The page text with columns separated into logical order.
    """
    words = page.extract_words()
    if not words:
        return page.extract_text() or ""

    threshold: Optional[float] = _detect_column_threshold(words)
    if threshold is None:
        return page.extract_text() or ""

    columns: dict[str, list] = {"left": [], "right": []}
    for word in words:
        key = "left" if word["x0"] <= threshold else "right"
        columns[key].append(word)

    page_lines: list[str] = []
    for key in ("left", "right"):
        column_words = columns[key]
        if not column_words:
            continue
        lines: dict[int, list] = defaultdict(list)
        for word in column_words:
            lines[round(word["top"] / 3) * 3].append(word)
        for top in sorted(lines):
            row = sorted(lines[top], key=lambda w: w["x0"])
            page_lines.append(_join_row(row))
    return "\n".join(page_lines)


def _detect_column_threshold(words: list) -> Optional[float]:
    """Detect a split line between two columns of text.

    Two-column templates render the sidebar's name, contact, and each skill
    chip as separate left-aligned lines, so every sidebar row starts at the
    same small ``x0`` while the main column's rows start further right.
    Grouping words into rows, clustering those row-start x values by gap size
    isolates the sidebar and main column. The mid-point between their x ranges
    is the column threshold. Clusters must contain enough words and enough
    distinct rows so a right-aligned date run on an otherwise single-column
    page is not mistaken for a column. Returns None for single-column pages.

    Args:
        words: The page's extracted word dictionaries.

    Returns:
        Optional[float]: The x threshold separating columns, or None.
    """
    rows: dict[int, list] = defaultdict(list)
    for word in words:
        rows[round(word["top"] / 3) * 3].append(word)
    row_min_x: dict[int, float] = {top: min(w["x0"] for w in row)
                                   for top, row in rows.items()}
    row_starts = sorted(set(row_min_x.values()))
    if len(row_starts) < 2:
        return None
    clusters: list[list] = [[row_starts[0]]]
    for current_pos, next_pos in zip(row_starts, row_starts[1:]):
        if next_pos - current_pos > COLUMN_GAP_PX:
            clusters.append([])
        clusters[-1].append(next_pos)

    left: Optional[tuple] = None
    right: Optional[tuple] = None
    for cluster in clusters:
        low, high = cluster[0], cluster[-1]
        cluster_rows = [
            row for top, row in rows.items() if low <= row_min_x[top] <= high
        ]
        cluster_words = [w for row in cluster_rows for w in row]
        if len(cluster_words) < MIN_COLUMN_WORDS or len(cluster_rows) < 2:
            continue
        if left is None:
            left = (low, high)
        elif right is None:
            right = (low, high)
            break
    if left is None or right is None:
        return None

    # The main column's leftmost row start marks its content edge.
    right_low = right[0]
    # The sidebar's right edge is the widest word that still starts to the left
    # of the main column. Words on a shared row that belong to the main column
    # (e.g. a section heading across from the sidebar heading) start at or
    # beyond ``right_low`` and are excluded.
    left_edge = max(
        (w["x1"] for w in words if w["x0"] < right_low), default=None
    )
    if left_edge is None or right_low - left_edge <= COLUMN_GAP_PX:
        return None
    return (left_edge + right_low) / 2.0


def _join_row(row: list) -> str:
    """Join a row's words, comma-separating words from distinct chips.

    Words within an inline-block chip (e.g. a skill badge) sit a few points
    apart, while chip boundaries leave a wider padding gap. Joining across that
    gap with a comma lets the skills parser split chips back into individual
    skills; prose words keep their normal single-space join.

    Args:
        row: The row's words sorted by x0.

    Returns:
        str: The joined row text.
    """
    output = ""
    for index, word in enumerate(row):
        if index == 0:
            output = word["text"]
        else:
            gap = word["x0"] - row[index - 1]["x1"]
            if CHIP_GAP_PX < gap <= CHIP_COMMA_MAX_PX:
                output += ", " + word["text"]
            else:
                output += " " + word["text"]
    return output


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
