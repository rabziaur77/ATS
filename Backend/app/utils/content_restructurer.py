"""
Module: content_restructurer.py
Created: 2026-09-03
Purpose: Section detection and normalization of raw CV text into structured JSON.
"""

import re
from typing import Optional

from app.schemas.resume import ParsedResumeData

SECTION_HEADINGS = {
    "summary": re.compile(
        r"^\s*(summary|profile|professional\s+summary|about\s*me|about|objective|career\s+objective)\s*[:]?\s*$",
        re.IGNORECASE,
    ),
    "experience": re.compile(
        r"^\s*(work\s+experience|experience|professional\s+experience|academic\s*&\s*professional\s+experience|academic\s+experience|employment\s+history|work\s+history|career)\s*[:]?\s*$",
        re.IGNORECASE,
    ),
    "education": re.compile(r"^\s*(education|academic\s+background|studies)\s*[:]?\s*$", re.IGNORECASE),
    "skills": re.compile(
        r"^\s*(skills|technical\s+skills|tech\s+stack|technical\s+stack|research\s+skills|core\s+competencies|competencies|technologies|tools)\s*[:]?\s*$",
        re.IGNORECASE,
    ),
    "certifications": re.compile(
        r"^\s*(certifications|certificates|licenses|professional\s+certifications)\s*[:]?\s*$",
        re.IGNORECASE,
    ),
    "languages": re.compile(r"^\s*(languages|language\s+proficiencies)\s*[:]?\s*$", re.IGNORECASE),
    "projects": re.compile(
        r"^\s*(projects|personal\s+projects|key\s+projects|selected\s+projects|selected\s+work)\s*[:]?\s*$",
        re.IGNORECASE,
    ),
    "contact": re.compile(r"^\s*(contact|contact\s+information|contact\s+details)\s*[:]?\s*$", re.IGNORECASE),
}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(
    r"(\+?\d[\d\s\-().]{7,}\d)"
)
DATE_RANGE_RE = re.compile(
    r"(?P<start>(?:"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\.?\s*\d{4}|"
    r"(?:january|february|march|april|june|july|august|september|october|november|december)\s+\d{4}|"
    r"\d{4}"
    r"))"
    r"(\s*[-–—]\s*)"
    r"(?P<end>(?:"
    r"(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)\.?\s*\d{4}|"
    r"(?:january|february|march|april|june|july|august|september|october|november|december)\s+\d{4}|"
    r"\d{4}|present|current|now|today"
    r"))",
    re.IGNORECASE,
)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")
CID_GLYPH_RE = re.compile(r"\(cid:\d+\)")
BULLET_PREFIX_RE = re.compile(r"^\s*(?:[•▪‣·‒–—]|\-)\s*")


def _clean_line(line: str) -> str:
    """Remove common PDF/DOCX extraction artifacts from a line.

    Chromium-rendered PDFs may expose list markers as ``(cid:NNN)`` glyphs, and
    DOCX bullets survive as a leading ``•``/``-``. Stripping these keeps
    headings and content lines recognizable to the section parsing logic.
    Inline ``•`` is preserved because the same glyph separates company/location
    and degree/GPA fields in generated layouts; descriptions strip it later.

    Args:
        line: A raw extracted line.

    Returns:
        str: The cleaned line.
    """
    line = CID_GLYPH_RE.sub("", line)
    line = BULLET_PREFIX_RE.sub("", line)
    return re.sub(r"\s{2,}", " ", line).strip()


def restructure(raw_text: str) -> ParsedResumeData:
    """Convert raw CV text into structured, normalized parsed data.

    Args:
        raw_text: Plain text extracted from an uploaded CV.

    Returns:
        ParsedResumeData: Structured resume with detected sections.
    """
    lines = [_clean_line(ln) for ln in raw_text.splitlines()]
    sections: dict[str, list[str]] = {}
    current: Optional[str] = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        heading = _detect_heading(stripped)
        if heading:
            current = heading
            sections.setdefault(current, [])
        elif current:
            sections[current].append(stripped)
        else:
            sections.setdefault("header", []).append(stripped)

    data = ParsedResumeData()
    _fill_personal_info(data, sections.get("header", []) + sections.get("contact", []))
    data.summary = _join_text(sections.get("summary", []))
    data.experience = _parse_experience(sections.get("experience", []))
    data.education = _parse_education(sections.get("education", []))
    data.skills = _parse_skills(sections.get("skills", []))
    data.certifications = sections.get("certifications", [])
    data.languages = _parse_skills(sections.get("languages", []))
    data.projects = _parse_projects(sections.get("projects", []))
    return data


def _detect_heading(line: str) -> Optional[str]:
    """Return the section key if a line is a recognized section heading.

    Args:
        line: A single trimmed line of CV text.

    Returns:
        Optional[str]: The matching section key, or None.
    """
    for key, pattern in SECTION_HEADINGS.items():
        if pattern.match(line):
            return key
    return None


def _fill_personal_info(data: ParsedResumeData, lines: list[str]) -> None:
    """Populate personal_info from header/contact lines using regex.

    Args:
        data: The parsed-data object to populate.
        lines: Header and contact section lines.
    """
    joined = "\n".join(lines)
    if not data.personal_info.name and lines:
        data.personal_info.name = lines[0]

    email = EMAIL_RE.search(joined)
    if email:
        data.personal_info.email = email.group(0)

    phone = PHONE_RE.search(joined)
    if phone:
        data.personal_info.phone = phone.group(0).strip()


def _join_text(lines: list[str]) -> str:
    """Join a list of lines into a single normalized paragraph.

    Args:
        lines: Text lines.

    Returns:
        str: Lines merged with spaces, or empty string.
    """
    return " ".join(l.strip() for l in lines).strip()


def _parse_experience(lines: list[str]) -> list:
    """Group experience lines into structured entries.

    Handles both the pipe-separated format
    ("Senior Developer | Tech Corp | 2021 - Present") and generated-layout
    formats where the title, dates, company, and description appear on separate
    lines (e.g. "Senior Developer" / "2021 - Present" / "Tech Corp · NYC").

    Args:
        lines: Lines under the experience heading.

    Returns:
        list[ExperienceItem]: Parsed experience entries.
    """
    entries: list = []
    current: Optional[dict] = None
    pending_company: Optional[str] = None

    def finalize() -> None:
        nonlocal current
        if current:
            entries.append(_finalize_experience(current))
            current = None

    def open_entry() -> dict:
        nonlocal current
        current = {
            "title": "",
            "company": "",
            "location": "",
            "start_date": "",
            "end_date": "",
            "description": "",
        }
        return current

    for line in lines:
        dates_m = DATE_RANGE_RE.search(line)
        is_role = _looks_like_role_line(line)

        if dates_m and (is_role or "|" in line):
            # Full role heading with dates on a single line (original format).
            finalize()
            entry = open_entry()
            _parse_role_line(line, entry)
            if pending_company and not entry["company"]:
                entry["company"] = pending_company
            pending_company = None
        elif dates_m:
            # Date-range-only line (generated layout): fill the current entry,
            # or move to a new one if the current entry already has dates.
            start = _normalize_year(dates_m.group("start"))
            end = _normalize_year(dates_m.group("end"))
            leftover = DATE_RANGE_RE.sub("", line).strip(" ,:;")
            if current and not current["start_date"]:
                current["start_date"], current["end_date"] = start, end
                if leftover and not current["company"]:
                    current["company"] = leftover
            elif current:
                finalize()
                entry = open_entry()
                entry["start_date"], entry["end_date"] = start, end
                if leftover and not entry["company"]:
                    entry["company"] = leftover
            else:
                entry = open_entry()
                entry["start_date"], entry["end_date"] = start, end
                if leftover and not entry["company"]:
                    entry["company"] = leftover
            if pending_company and current and not current["company"]:
                current["company"] = pending_company
                pending_company = None
        elif is_role:
            if current and current["start_date"] and not current["title"]:
                # Generated layout with company/dates before the title.
                _parse_role_line(line, current)
            else:
                finalize()
                open_entry()
                _parse_role_line(line, current)
            if pending_company and current and not current["company"]:
                current["company"] = pending_company
                pending_company = None
        elif current and not current["company"] and _looks_like_company_line(line):
            company, location = _split_company_location(line)
            current["company"] = company or current["company"]
            current["location"] = location or current["location"]
        elif _looks_like_company_line(line):
            pending_company = _split_company_location(line)[0]
        elif current:
            current["description"] = (current["description"] + " " + line).strip()

    finalize()
    return entries


def _looks_like_company_line(line: str) -> bool:
    """Detect a standalone company/location line in generated layouts.

    Generated templates render the company on its own short, unpunctuated line
    (e.g. "Tech Corp", "Tech Corp · New York, NY"). Description sentences end
    with a period/question mark, so a short unpunctuated line is treated as a
    company line when the current entry still lacks one.

    Args:
        line: A line of text.

    Returns:
        bool: True if the line is a plausible company/location line.
    """
    if DATE_RANGE_RE.search(line) or _looks_like_role_line(line):
        return False
    stripped = line.strip()
    if not stripped or len(stripped) > 60:
        return False
    if re.search(r"[.!?]\s*$", stripped):
        return False
    return len(stripped.split()) <= 10


def _split_company_location(line: str) -> tuple[str, str]:
    """Split a company · location line into its two parts.

    Args:
        line: A line like "Tech Corp" or "Tech Corp · New York, NY".

    Returns:
        tuple[str, str]: (company, location) with empty strings as needed.
    """
    parts = [p.strip() for p in re.split(r"[·•|–]|\s+-\s+", line) if p.strip()]
    if not parts:
        return "", ""
    if len(parts) >= 2 and _looks_like_location(parts[-1]):
        return parts[0], parts[-1]
    return parts[0], ""


def _looks_like_location(value: str) -> bool:
    """Heuristic for whether a trailing company-line segment is a location.

    Args:
        value: A candidate location string.

    Returns:
        bool: True if it reads like a city/state/remote descriptor.
    """
    loc = value.strip(" ,")
    if not loc:
        return False
    lowered = loc.lower()
    if any(word in lowered for word in ("remote", "hybrid", "on-site")):
        return True
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z .-]*,\s*[A-Za-z .]{2,30}", loc))


ROLE_KEYWORDS = ("engineer", "developer", "manager", "lead", "analyst", "consultant",
                 "director", "head of", "specialist", "officer", "intern", "associate",
                 "architect", "designer", "administrator", "scientist", "coordinator",
                 "supervisor")
ROLE_KEYWORD_PATTERNS = tuple(
    re.compile(r"\b" + keyword.replace(" ", r"\s+") + r"\b")
    for keyword in ROLE_KEYWORDS
)
ROLE_PREFIX_WORDS = frozenset({
    "senior", "lead", "principal", "staff", "junior", "chief", "vice", "head",
    "software", "front", "front-end", "frontend", "back", "back-end", "backend",
    "full", "full-stack", "fullstack", "web", "mobile", "devops", "data", "qa",
    "product", "project", "system", "sales", "marketing", "business", "ux", "ui",
    "cloud", "security", "network", "site", "technical", "associate", "executive",
    "python", "java", "devops",
})


def _looks_like_role_line(line: str) -> bool:
    """Heuristically detect a role heading line.

    A role line typically has '|' separators (title | company | dates), a title
    word early in the line like "Senior Developer", or a multi-word title that
    starts with a role qualifier like "Senior Software Engineer". Description
    lines are sentences, so we avoid matching when the line is clearly prose.
    Keywords are matched on word boundaries so company names containing role
    words (e.g. "Stari Engineering") do not start a new role.

    Args:
        line: A line of text.

    Returns:
        bool: True if the line appears to start a new role.
    """
    if "|" in line:
        return True
    lowered = line.lower()
    words = lowered.split()
    if words and words[0].strip(".,;:") in ROLE_PREFIX_WORDS:
        # "Senior Software Engineer", "Technical Product Manager", ...
        snapshot = lowered[:80]
        if any(pattern.search(snapshot) for pattern in ROLE_KEYWORD_PATTERNS):
            return True
    # Require a keyword near the start (role heading), not mid-sentence (prose).
    for pattern in ROLE_KEYWORD_PATTERNS:
        match = pattern.search(lowered)
        if match and match.start() <= 12:
            return True
    return False


def _parse_role_line(line: str, current: dict) -> None:
    """Extract title/company/location and dates from a role line.

    Pipe-separated headings may be ordered either "Title | Company | Dates"
    or "Company | Title | Dates". The segment that reads like a role heading
    wins the title slot and the other becomes the company; a trailing location
    segment is pulled off the end regardless of order.

    Args:
        line: A role heading line.
        current: The entry dict being built.
    """
    m = DATE_RANGE_RE.search(line)
    if m:
        current["start_date"] = _normalize_year(m.group("start"))
        current["end_date"] = _normalize_year(m.group("end"))
        line = DATE_RANGE_RE.sub("", line)

    parts = [p.strip() for p in line.split("|") if p.strip()]

    # Trailing location segment ("... | New York, NY").
    if len(parts) >= 2 and _looks_like_location(parts[-1]):
        current["location"] = parts.pop().strip(" ,")

    if len(parts) >= 2:
        # Disambiguate "Title | Company" from "Company | Title". When a single
        # segment clearly reads as a role heading, the other is the company;
        # any other case falls back to the title-first ordering.
        title_is_first = _looks_like_role_line(parts[0])
        company_is_first = _looks_like_role_line(parts[1])
        if company_is_first and not title_is_first:
            current["company"] = _strip_trailing_dash(parts[0]).strip(" ,")
            current["title"] = _strip_trailing_dash(parts[1]).strip(" ,")
        else:
            current["title"] = _strip_trailing_dash(parts[0]).strip(" ,")
            current["company"] = _strip_trailing_dash(parts[1]).strip(" ,")
    elif parts:
        current["title"] = _strip_trailing_dash(parts[0]).strip(" ,")
        if "·" in parts[0] and not current["location"]:
            # Generated layouts put the designation and location on the
            # sub-line ("Senior Developer · New York, NY").
            title, _, tail = parts[0].partition("·")
            tail = tail.strip().strip(" ,")
            if title.strip() and _looks_like_location(tail):
                current["title"] = title.strip().strip(" ,")
                current["location"] = tail


def _finalize_experience(current: dict):
    """Return an ExperienceItem from a raw entry dict.

    Args:
        current: Raw experience entry data.

    Returns:
        ExperienceItem: Fully formed experience item.
    """
    description = re.sub(r"\s*•\s*", " ", current["description"])
    current["description"] = description.strip()
    from app.schemas.resume import ExperienceItem  # local import to avoid cycle

    return ExperienceItem(**current)


def _parse_education(lines: list[str]) -> list:
    """Group education lines into structured entries.

    Handles the pipe-separated format ("B.S. Computer Science | MIT, 2015-2019")
    and generated-layout formats where the institution, dates, and degree
    appear on separate lines (e.g. "MIT" / "2015 - 2019" /
    "B.S. Computer Science · GPA: 3.8").

    Args:
        lines: Lines under the education heading.

    Returns:
        list[EducationItem]: Parsed education entries.
    """
    entries: list = []
    current: Optional[dict] = None
    pending_institution: Optional[str] = None

    def finalize() -> None:
        nonlocal current
        if current:
            entries.append(_finalize_education(current))
            current = None

    def open_entry() -> dict:
        nonlocal current
        current = {
            "institution": "",
            "degree": "",
            "start_date": "",
            "end_date": "",
            "gpa": "",
        }
        return current

    for line in lines:
        dates_m = DATE_RANGE_RE.search(line)
        if _looks_like_education_heading(line):
            # Degree-bearing line starts (or fills) an entry.
            if current and not current["degree"] and current["institution"]:
                _parse_education_line(line, current)
            else:
                finalize()
                open_entry()
                if pending_institution and not current["institution"]:
                    current["institution"] = pending_institution
                    pending_institution = None
                _parse_education_line(line, current)
            gpa_m = re.search(r"gpa[: ]+([\d.]+)", line, re.IGNORECASE)
            if gpa_m:
                current["gpa"] = gpa_m.group(1)
        elif dates_m:
            start = _normalize_year(dates_m.group("start"))
            end = _normalize_year(dates_m.group("end"))
            leftover = DATE_RANGE_RE.sub("", line).strip(" ,:;.")
            if current and not current["start_date"]:
                current["start_date"], current["end_date"] = start, end
                if leftover and not current["institution"]:
                    current["institution"] = leftover
            elif pending_institution:
                finalize()
                entry = open_entry()
                entry["institution"] = pending_institution
                entry["start_date"], entry["end_date"] = start, end
                pending_institution = None
                if leftover and not entry["institution"]:
                    entry["institution"] = leftover
            else:
                if current:
                    finalize()
                entry = open_entry()
                entry["start_date"], entry["end_date"] = start, end
                if leftover and not entry["institution"]:
                    entry["institution"] = leftover
        elif "gpa" in line.lower():
            gpa_m = re.search(r"gpa[: ]+([\d.]+)", line, re.IGNORECASE)
            if gpa_m and current:
                current["gpa"] = gpa_m.group(1)
        elif _looks_like_institution_line(line):
            if current and current["start_date"] and not current["institution"]:
                current["institution"] = line
            elif current and current["degree"] and not current["institution"]:
                current["institution"] = line
            else:
                pending_institution = line
        elif current:
            current["degree"] = (current["degree"] + " " + line).strip()

    if pending_institution and current and not current["institution"]:
        current["institution"] = pending_institution
    elif pending_institution and current and current["degree"]:
        current["degree"] = (current["degree"] + " " + pending_institution).strip()
    if current and current["degree"] and not current["institution"]:
        current["institution"] = _clean_degree(current["degree"])
    finalize()
    return entries


def _looks_like_institution_line(line: str) -> bool:
    """Detect a bare institution line in generated layouts.

    Generated templates render the institution on its own short, unpunctuated
    line (e.g. "MIT", "Stanford University"). Such lines carry no degree
    keywords, role keywords, or date ranges.

    Args:
        line: A line of text.

    Returns:
        bool: True if the line reads like a standalone institution name.
    """
    if DATE_RANGE_RE.search(line) or _looks_like_role_line(line):
        return False
    if re.search(
        r"(degree|b\.?s\.?|b\.?a\.?|m\.?s\.?|m\.?a\.?|ph\.?d|bachelor|master|diploma)",
        line,
        re.IGNORECASE,
    ):
        return False
    stripped = line.strip()
    if not stripped or len(stripped) > 60:
        return False
    if re.search(r"[.!?]\s*$", stripped):
        return False
    return len(stripped.split()) <= 8


def _looks_like_education_heading(line: str) -> bool:
    """Detect a line that starts a new education entry.

    Matches lines containing a degree keyword or a '|' separator.

    Args:
        line: A line of text.

    Returns:
        bool: True if the line starts a new education entry.
    """
    if "|" in line:
        return True
    return bool(
        re.search(
            r"(degree|b\.?s\.?|b\.?a\.?|m\.?s\.?|m\.?a\.?|ph\.?d|bachelor|master|diploma)",
            line,
            re.IGNORECASE,
        )
    )


def _parse_education_line(line: str, current: dict) -> None:
    """Extract degree, institution, and dates from an education line.

    Args:
        line: An education heading line.
        current: The entry dict being built.
    """
    m = DATE_RANGE_RE.search(line)
    if m:
        current["start_date"] = _normalize_year(m.group("start"))
        current["end_date"] = _normalize_year(m.group("end"))
        line = DATE_RANGE_RE.sub("", line)

    parts = [p.strip() for p in line.split("|") if p.strip()]
    if len(parts) >= 2:
        current["degree"] = _clean_degree(parts[0])
        current["institution"] = parts[1].strip(", ")
    elif parts:
        current["degree"] = _clean_degree(parts[0])


def _strip_trailing_dash(value: str) -> str:
    """Remove an artifact dash left by an empty rendered date range.

    Args:
        value: A raw string that may end with a standalone dash.

    Returns:
        str: The string without a trailing dash separator.
    """
    return re.sub(r"\s*[-–—]\s*$", "", value)


def _clean_degree(degree: str) -> str:
    """Trim GPA/date annotations that often trail a rendered degree line.

    Args:
        degree: A raw degree string.

    Returns:
        str: The degree without a trailing "· GPA: 3.8" annotation or dash.
    """
    cleaned = re.sub(r"\s*[·•|]\s*GPA.*$", "", degree, flags=re.IGNORECASE)
    return _strip_trailing_dash(cleaned).strip(" ,")


def _finalize_education(current: dict):
    """Return an EducationItem from a raw education dict.

    Args:
        current: Raw education entry data.

    Returns:
        EducationItem: Fully formed education item.
    """
    from app.schemas.resume import EducationItem  # local import to avoid cycle

    return EducationItem(**current)


def _parse_skills(lines: list[str]) -> list[str]:
    """Parse the skills section into a flat list of skills.

    Args:
        lines: Lines under the skills heading.

    Returns:
        list[str]: Deduplicated, ordered skill names.
    """
    skills: list[str] = []
    for line in lines:
        for part in re.split(r"[,;•|]", line):
            part = part.strip().lstrip("-•").strip()
            if part and part.lower() not in [s.lower() for s in skills]:
                skills.append(part)
    return skills


def _parse_projects(lines: list[str]) -> list[dict]:
    """Parse the projects section into a simple list of dicts.

    Args:
        lines: Lines under the projects heading.

    Returns:
        list[dict]: Each project as {'name': ...}.
    """
    return [{"name": line} for line in lines if line.strip()]


def _normalize_year(value: str) -> str:
    """Return a 4-digit year if recognizable in the value.

    Args:
        value: A date string (possibly with month names).

    Returns:
        str: The 4-digit year if found, otherwise the original value.
    """
    m = YEAR_RE.search(value)
    if m:
        return m.group(0)
    return value
