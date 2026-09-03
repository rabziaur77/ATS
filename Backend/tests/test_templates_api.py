"""
Module: test_templates_api.py
Created: 2026-09-03
Purpose: Tests for template listing, custom template CRUD, and sandboxing.
"""

from pathlib import Path


def _upload(client, session_id="sess"):
    with open(
        Path(__file__).parent / "fixtures" / "sample_cv.txt", "rb"
    ) as f:
        return client.post(
            "/api/upload/cv",
            files={"file": ("sample_cv.txt", f, "text/plain")},
            headers={"x-session-id": session_id},
        )


def test_create_custom_and_generate(client):
    up = _upload(client)
    rid = up.json()["id"]

    html = (
        "{% extends '_base.html' %}{% block styles %}"
        "body { font-family: Arial; }{% endblock %}"
    )
    resp = client.post(
        "/api/templates/custom",
        json={
            "name": "My Custom",
            "config": {"accent_color": "#ff0000", "section_order": ["summary"]},
            "html_template": html,
        },
        headers={"x-session-id": "sess"},
    )
    assert resp.status_code == 201, resp.text
    ctid = resp.json()["id"]

    g = client.post(
        f"/api/resume/{rid}/generate",
        json={"template_id": str(ctid), "format": "html"},
        headers={"x-session-id": "sess"},
    )
    assert g.status_code == 201, g.text


def test_create_custom_rejects_unsafe(client):
    dangerous = (
        "{% extends '_base.html' %}"
        "{{ cycler.__class__.__mro__[1].__subclasses__() }}"
    )
    resp = client.post(
        "/api/templates/custom",
        json={"name": "Bad", "html_template": dangerous},
        headers={"x-session-id": "sess"},
    )
    assert resp.status_code == 422


def test_custom_template_scoped_to_session(client):
    resp = client.post(
        "/api/templates/custom",
        json={"name": "Owner Only", "config": {}, "html_template": "{{ name }}"},
        headers={"x-session-id": "owner"},
    )
    assert resp.status_code == 201
    ctid = resp.json()["id"]

    listed = client.get(
        "/api/templates", headers={"x-session-id": "intruder"}
    ).json()["items"]
    assert all(int(item["id"]) != ctid for item in listed if item["is_custom"])
