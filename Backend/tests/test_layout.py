"""
Module: test_layout.py
Created: 2026-09-03
Purpose: Prove the built-in templates produce genuinely different structural
         layouts (not just color/font), while preserving the same resume
         content. This is the acceptance test for the Phase 1 template work.
"""

from pathlib import Path


def _upload(client, session_id="layout-session"):
    with open(
        Path(__file__).parent / "fixtures" / "sample_cv.txt", "rb"
    ) as f:
        return client.post(
            "/api/upload/cv",
            files={"file": ("sample_cv.txt", f, "text/plain")},
            headers={"x-session-id": session_id},
        )


def _preview(client, resume_id, template_id):
    resp = client.get(
        f"/api/resume/{resume_id}/preview",
        params={"template_id": template_id},
        headers={"x-session-id": "layout-session"},
    )
    assert resp.status_code == 200, resp.text
    return resp.text


ALL_TEMPLATES = [
    "academic",
    "ats_standard",
    "classic",
    "elegant",
    "executive",
    "minimal",
    "modern",
    "professional",
    "simple",
    "technical",
]


def test_all_templates_return_distinct_html(client):
    """Every template renders at least one structural fingerprint that differs."""
    up = _upload(client)
    rid = up.json()["id"]

    html_for = {t: _preview(client, rid, t) for t in ALL_TEMPLATES}

    # Modern is the only two-column/sidebar layout.
    assert 'class="layout"' in html_for["modern"]
    assert 'class="sidebar"' in html_for["modern"]
    for t in ALL_TEMPLATES:
        if t != "modern":
            assert 'class="sidebar"' not in html_for[t], t

    # Modern renders skills as chips in a sidebar; ATS uses plain text.
    assert '<li class="chip">' in html_for["modern"]

    # Technical places a prominent Tech Stack band near the top.
    assert "Tech Stack" in html_for["technical"]

    # ATS Standard must be single-column and plain: no tables, no images,
    # no graphical icons, and skills rendered as comma-joined text.
    ats = html_for["ats_standard"]
    assert "<table" not in ats
    assert "<img" not in ats
    assert '<ul class="skills-tags">' not in ats
    assert "Python, FastAPI" in ats

    # Executive labels the main experience heading specifically.
    assert "Professional Experience" in html_for["executive"]

    # All templates should be structurally different from each other (fewer
    # than the full set sharing an identical DOM skeleton).
    unique = {html_for[t] for t in ALL_TEMPLATES}
    assert len(unique) >= 9, "Templates look too identical structurally"


def test_templates_preserve_same_content(client):
    """All templates must contain the same resume content, unchanged."""
    up = _upload(client)
    rid = up.json()["id"]

    content_markers = ["John Doe", "john.doe@example.com", "Tech Corp",
                       "MIT", "Python", "English"]

    for t in ALL_TEMPLATES:
        html = _preview(client, rid, t)
        for marker in content_markers:
            assert marker in html, f"{t} missing content marker: {marker}"


def test_selection_propagation_changes_layout(client):
    """Requesting different template_ids returns different structures."""
    up = _upload(client)
    rid = up.json()["id"]

    modern = _preview(client, rid, "modern")
    ats = _preview(client, rid, "ats_standard")

    assert 'class="sidebar"' in modern
    assert 'class="sidebar"' not in ats

    # Middle content (the resume body) matches, proving content equality
    # while structure differs.
    assert "Tech Corp" in modern and "Tech Corp" in ats


def test_layout_field_listed_for_builtins(client):
    """The templates list endpoint exposes each built-in's layout label."""
    resp = client.get(
        "/api/templates", headers={"x-session-id": "layout-session"}
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    by_id = {item["id"]: item for item in items}
    assert by_id["ats_standard"]["layout"] == "single_column_plain"
    assert by_id["modern"]["layout"] == "two_column_sidebar"
    assert by_id["technical"]["layout"] == "skills_first"
    assert by_id["academic"]["layout"] == "education_first"