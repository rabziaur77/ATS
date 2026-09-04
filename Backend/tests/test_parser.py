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


def _restructure(text: str):
    from app.utils.content_restructurer import restructure

    return restructure(text)


def test_parse_generated_layout_title_dates_company_desc():
    """A generated single-line-per-field layout still yields one entry/block."""
    text = (
        "John Doe\njohn@example.com | 555\n"
        "Summary\nExperienced engineer.\n"
        "Experience\n"
        "Senior Developer\n2021 - Present\nTech Corp · New York, NY\n"
        "Led a team. Built CI/CD.\n"
        "Developer\n2018 - 2021\nStartup Inc\nBuilt web apps.\n"
        "Education\nMIT\n2015 - 2019\nB.S. Computer Science · GPA: 3.8\n"
    )
    data = _restructure(text)
    assert [(e.title, e.company, e.location, e.start_date, e.end_date) for e in data.experience] == [
        ("Senior Developer", "Tech Corp", "New York, NY", "2021", "Present"),
        ("Developer", "Startup Inc", "", "2018", "2021"),
    ]
    assert data.experience[0].description == "Led a team. Built CI/CD."
    assert [(e.institution, e.degree, e.gpa) for e in data.education] == [
        ("MIT", "B.S. Computer Science", "3.8")
    ]


def test_parse_generated_layout_company_first():
    """A generated layout with company & dates before the title is grouped."""
    text = (
        "Ziaur Rab\nz@example.com\n"
        "Experience\n"
        "EPAM Systems\n2023 - Present\nSenior Software Engineer\n"
        "Develop enterprise applications.\n"
    )
    data = _restructure(text)
    assert [(e.title, e.company, e.start_date, e.end_date) for e in data.experience] == [
        ("Senior Software Engineer", "EPAM Systems", "2023", "Present")
    ]


def test_parse_generated_education_two_line_degree():
    """Degree and GPA on a separate line merge into the pending entry."""
    text = (
        "MIT\n2015 - 2019\nB.S. Computer Science\nGPA: 3.8\n"
    )
    data = _restructure("X\nx@e.com\nEducation\n" + text)
    assert [(e.institution, e.degree, e.gpa, e.start_date, e.end_date)
            for e in data.education] == [
        ("MIT", "B.S. Computer Science", "3.8", "2015", "2019")
    ]


def test_parse_custom_template_headings():
    """Built-in template headings that differ from the standard set map to sections."""
    text = (
        "John Doe\njohn@example.com | 555\n"
        "About\nI am a developer.\n"
        "Tech Stack\nPython, Go\n"
        "Academic & Professional Experience\nLead | ACME | 2020 - 2023\nDid stuff.\n"
        "Research Skills\nRust\n"
        "Selected Projects\nBenchmarker\n"
    )
    data = _restructure(text)
    assert data.summary == "I am a developer."
    assert "Python" in data.skills and "Rust" in data.skills
    assert [(e.title, e.company) for e in data.experience] == [("Lead", "ACME")]
    assert data.projects == [{"name": "Benchmarker"}]


def test_parse_cid_and_bullet_glyph_artifacts():
    """PDF/DOCX list glyphs and (cid:NNN) markers are stripped before parsing."""
    text = (
        "Ziaur Rab\nz@example.com\n"
        "Experience\n"
        "EPAM Systems\n2023 - Present\nSenior Software Engineer\n"
        "(cid:127) Develop enterprise apps.\n"
        "Skills\n(cid:127) Python"
    )
    data = _restructure(text)
    assert data.experience[0].description == "Develop enterprise apps."
    assert data.skills == ["Python"]


def test_parse_experience_company_on_date_line():
    """A 'Company 2023 - Present' heading line keeps its company name."""
    text = (
        "Ziaur Rab\nz@example.com\n"
        "Experience\n"
        "EPAM Systems 2023 - Present\nSenior Software Engineer\n"
        "Develop enterprise applications.\n"
    )
    data = _restructure(text)
    assert [(e.title, e.company, e.start_date, e.end_date) for e in data.experience] == [
        ("Senior Software Engineer", "EPAM Systems", "2023", "Present")
    ]


def test_parse_experience_engineering_company_not_role():
    """A company whose name contains 'engineering' is not parsed as a role."""
    text = (
        "Ziaur Rab\nz@example.com\n"
        "Experience\n"
        "Stari Engineering 2018 - 2021\nSenior Software Engineer\n"
        "Built insurance CRM.\n"
        "Accurate App Solution 2016 - 2018\nSoftware Engineer\n"
        "Developed HRIS.\n"
    )
    data = _restructure(text)
    assert [(e.title, e.company, e.start_date, e.end_date) for e in data.experience] == [
        ("Senior Software Engineer", "Stari Engineering", "2018", "2021"),
        ("Software Engineer", "Accurate App Solution", "2016", "2018"),
    ]


def test_parse_experience_inline_bullets_removed():
    """Inline bullet markers inside a description are stripped."""
    text = (
        "Ziaur Rab\nz@example.com\n"
        "Experience\n"
        "Senior Developer | Tech Corp | 2021 - Present\n"
        "• Develop enterprise apps. • Built REST APIs. • Wrote tests.\n"
    )
    data = _restructure(text)
    assert data.experience[0].description == (
        "Develop enterprise apps. Built REST APIs. Wrote tests."
    )


def test_parse_education_trailing_dash_stripped():
    """A degree line ending in an empty-date dash is cleaned."""
    text = (
        "Ziaur Rab\nz@example.com\n"
        "Education\n"
        "Bachelor of Science in Computer Science -\n"
    )
    data = _restructure(text)
    assert data.education[0].degree == "Bachelor of Science in Computer Science"
    assert data.education[0].institution == "Bachelor of Science in Computer Science"


def test_parse_experience_company_first_with_location():
    """Company-first layout: designation on the sub-line splits off the location."""
    text = (
        "Ziaur Rab\nz@example.com\n"
        "Experience\n"
        "Tech Corp 2021 - Present\nSenior Developer · New York, NY\n"
        "Led a team building REST APIs.\n"
        "Startup Inc 2018 - 2021\nDeveloper\n"
        "Built web apps.\n"
    )
    data = _restructure(text)
    assert [(e.title, e.company, e.location, e.start_date, e.end_date) for e in data.experience] == [
        ("Senior Developer", "Tech Corp", "New York, NY", "2021", "Present"),
        ("Developer", "Startup Inc", "", "2018", "2021"),
    ]
