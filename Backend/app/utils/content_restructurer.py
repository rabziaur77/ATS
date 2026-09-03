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
        r"^\s*(summary|profile|professional\s+summary|about\s*me|objective|career\s+objective)\s*[:]?\s*$",
        re.IGNORECASE,
    ),
    "experience": re.compile(
        r"^\s*(work\s+experience|experience|professional\s+experience|employment\s+history|work\s+history|career)\s*[:]?\s*$",
        re.IGNORECASE,
    ),
    "education": re.compile(r"^\s*(education|academic\s+background|studies)\s*[:]?\s*$", re.IGNORECASE),
    "skills": re.compile(
        r"^\s*(skills|technical\s+skills|core\s+competencies|competencies|technologies|tools)\s*[:]?\s*$",
        re.IGNORECASE,
    ),
    "certifications": re.compile(
        r"^\s*(certifications|certificates|licenses|professional\s+certifications)\s*[:]?\s*$",
        re.IGNORECASE,
    ),
    "languages": re.compile(r"^\s*(languages|language\s+proficiencies)\s*[:]?\s*$", re.IGNORECASE),
    "projects": re.compile(r"^\s*(projects|personal\s+projects|key\s+projects)\s*[:]?\s*$", re.IGNORECASE),
    "contact": re.compile(r"^\s*(contact|contact\s+information|contact\s+details)\s*[:]?\s*$", re.IGNORECASE),
}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(
    r"(\+?\d[\d\s\-().]{7,}\d)"
)
DATE_RANGE_RE = re.compile(r"(?P<start>[A-Za-z]{3,9}\.\s?\d{4}|\d{4}|[A-Za-z]{3,9}\s\d{4})(\s*[-–—]\s*)(?P<end>[A-Za-z]{3,9}\.\s?\d{4}|\d{4}|[A-Za-z]{3,9}\s\d{4}|present|current|now|today)", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


def restructure(raw_text: str) -> ParsedResumeData:
    """Convert raw CV text into structured, normalized parsed data.

    Args:
        raw_text: Plain text extracted from an uploaded CV.

    Returns:
        ParsedResumeData: Structured resume with detected sections.
    """
    lines = [ln.rstrip() for ln in raw_text.splitlines()]
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

    A new entry starts when a line contains a date range or looks like a
    role/title heading (not a plain description).

    Args:
        lines: Lines under the experience heading.

    Returns:
        list[ExperienceItem]: Parsed experience entries.
    """
    entries: list = []
    current: Optional[dict] = None

    for line in lines:
        if DATE_RANGE_RE.search(line) or _looks_like_role_line(line):
            if current:
                entries.append(_finalize_experience(current))
            current = {
                "title": "",
                "company": "",
                "location": "",
                "start_date": "",
                "end_date": "",
                "description": "",
            }
            _parse_role_line(line, current)
        elif current:
            current["description"] = (current["description"] + " " + line).strip()

    if current:
        entries.append(_finalize_experience(current))
    return entries


def _looks_like_role_line(line: str) -> bool:
    """Heuristically detect a role heading line.

    A role line typically has '|' separators (title | company | dates) or a
    title word early in the line like "Senior Developer". Description lines
    are sentences, so we avoid matching when the line is clearly prose.

    Args:
        line: A line of text.

    Returns:
        bool: True if the line appears to start a new role.
    """
    if "|" in line:
        return True
    lowered = line.lower()
    keywords = ("engineer", "developer", "manager", "lead", "analyst", "consultant",
                "director", "head of", "specialist", "officer", "intern", "associate")
    # Require a keyword near the start (role heading), not mid-sentence (prose).
    for kw in keywords:
        idx = lowered.find(kw)
        if idx != -1 and idx <= 12:
            return True
    return False


def _parse_role_line(line: str, current: dict) -> None:
    """Extract title/company/location and dates from a role line.

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
    if parts:
        current["title"] = parts[0]
    if len(parts) >= 2:
        current["company"] = parts[1]
    if len(parts) >= 3:
        current["location"] = parts[2]


def _finalize_experience(current: dict):
    """Return an ExperienceItem from a raw entry dict.

    Args:
        current: Raw experience entry data.

    Returns:
        ExperienceItem: Fully formed experience item.
    """
    current["description"] = current["description"].strip()
    from app.schemas.resume import ExperienceItem  # local import to avoid cycle

    return ExperienceItem(**current)


def _parse_education(lines: list[str]) -> list:
    """Group education lines into structured entries.

    Args:
        lines: Lines under the education heading.

    Returns:
        list[EducationItem]: Parsed education entries.
    """
    entries: list = []
    current: Optional[dict] = None

    for line in lines:
        if _looks_like_education_heading(line):
            if current:
                entries.append(_finalize_education(current))
            current = {
                "institution": "",
                "degree": "",
                "start_date": "",
                "end_date": "",
                "gpa": "",
            }
            _parse_education_line(line, current)
        elif current:
            m = DATE_RANGE_RE.search(line)
            if m:
                current["start_date"] = _normalize_year(m.group("start"))
                current["end_date"] = _normalize_year(m.group("end"))
            elif "gpa" in line.lower():
                gpa_m = re.search(r"gpa[: ]+([\d.]+)", line, re.IGNORECASE)
                if gpa_m:
                    current["gpa"] = gpa_m.group(1)
            else:
                current["degree"] = (current["degree"] + " " + line).strip()

    if current:
        entries.append(_finalize_education(current))
    return entries


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
        current["degree"] = parts[0].strip(", ")
        current["institution"] = parts[1].strip(", ")
    elif parts:
        current["degree"] = parts[0].strip(", ")
        if not current["institution"]:
            current["institution"] = parts[0].strip(", ")


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
