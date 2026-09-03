"""
Module: resume_processor.py
Created: 2026-09-03
Purpose: Restructures parsed resume data to match a template's layout
         config (section order, content density) for rendering.
"""

from typing import Any

from app.schemas.resume import ParsedResumeData

DEFAULT_SECTION_ORDER = [
    "summary",
    "experience",
    "education",
    "skills",
    "certifications",
    "projects",
    "languages",
]


def process(data: ParsedResumeData, config: dict) -> dict:
    """Prepare parsed data for template rendering.

    Args:
        data: Structured parsed resume data.
        config: The selected template's layout configuration.

    Returns:
        dict: Template-ready data with ordered sections and a flags hint.
    """
    order = config.get("section_order", DEFAULT_SECTION_ORDER)
    if not order or not isinstance(order, list):
        order = DEFAULT_SECTION_ORDER

    available = {
        "summary": bool(data.summary),
        "experience": bool(data.experience),
        "education": bool(data.education),
        "skills": bool(data.skills),
        "certifications": bool(data.certifications),
        "projects": bool(data.projects),
        "languages": bool(data.languages),
    }

    ordered: list[dict] = []
    for section in order:
        if available.get(section):
            ordered.append({"key": section, "title": _section_title(section)})
        elif section not in available:
            ordered.append({"key": section, "title": _section_title(section)})

    # Preserve unknown (custom) sections listed in order so custom templates work.
    for key in order:
        if not any(o["key"] == key for o in ordered):
            ordered.append({"key": key, "title": _section_title(key)})

    return {
        "personal_info": _dict_of(data.personal_info),
        "summary": data.summary,
        "experience": [_dict_of(e) for e in data.experience],
        "education": [_dict_of(e) for e in data.education],
        "skills": data.skills,
        "certifications": data.certifications,
        "languages": data.languages,
        "projects": data.projects,
        "sections": ordered,
        "config": config,
    }


def _dict_of(obj: Any) -> dict:
    """Convert a Pydantic model (or dict) to a plain dict.

    Args:
        obj: A pydantic BaseModel instance or a dict.

    Returns:
        dict: The model's fields as a dict.
    """
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if isinstance(obj, dict):
        return obj
    return dict(obj)


def _section_title(key: str) -> str:
    """Human-readable title for a section key.

    Args:
        key: Section identifier (e.g. 'experience').

    Returns:
        str: Title-cased label (e.g. 'Experience').
    """
    return key.replace("_", " ").title()
