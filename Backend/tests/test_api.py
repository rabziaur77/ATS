"""
Module: test_api.py
Created: 2026-09-03
Purpose: End-to-end API tests covering upload, templates, generation, and scope.
"""

import os


def _upload(client, session_id="test-session"):
    with open(
        os.path.join(os.path.dirname(__file__), "fixtures", "sample_cv.txt"), "rb"
    ) as f:
        return client.post(
            "/api/upload/cv",
            files={"file": ("sample_cv.txt", f, "text/plain")},
            headers={"x-session-id": session_id},
        )


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_upload_parses_cv(client):
    resp = _upload(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["filename"] == "sample_cv.txt"
    assert body["file_type"] == "txt"
    assert "Python" in body["parsed_data"]["skills"]


def test_list_templates_includes_builtins(client):
    resp = client.get("/api/templates", headers={"x-session-id": "test-session"})
    assert resp.status_code == 200
    names = {item["id"] for item in resp.json()["items"]}
    for expected in ("classic", "modern", "minimal", "ats_standard"):
        assert expected in names


def test_generate_realistic_types(client):
    """Known-flaky but useful: pdfs/docx/html generation basic sanity."""
    up = _upload(client)
    resume_id = up.json()["id"]

    for fmt in ("html", "pdf", "docx"):
        resp = client.post(
            f"/api/resume/{resume_id}/generate",
            json={"template_id": "modern", "format": fmt},
            headers={"x-session-id": "test-session"},
        )
        assert resp.status_code == 201, (fmt, resp.text)
        assert resp.json()["format"] == fmt


def test_generate_preview(client):
    up = _upload(client)
    resume_id = up.json()["id"]
    resp = client.get(
        f"/api/resume/{resume_id}/preview",
        params={"template_id": "modern"},
        headers={"x-session-id": "test-session"},
    )
    assert resp.status_code == 200
    assert "John Doe" in resp.text


def test_scoping_blocks_other_session(client):
    up = _upload(client, session_id="owner-session")
    resume_id = up.json()["id"]
    resp = client.get(
        f"/api/resume/{resume_id}",
        headers={"x-session-id": "other-session"},
    )
    assert resp.status_code == 404
