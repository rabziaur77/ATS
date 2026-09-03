"""
Module: docx_generator.py
Created: 2026-09-03
Purpose: Thin wrapper emitting DOCX resumes via the shared render engine.
"""

from pathlib import Path

from app.services.html_generator import render_docx


def generate_docx(
    template_source: str,
    data: dict,
    config: dict,
    output_path: Path,
    sandbox: bool = True,
    loader_dir: str | None = None,
) -> Path:
    """Generate a DOCX resume.

    Args:
        template_source: Jinja2 HTML template source.
        data: Template-ready resume data.
        config: Template layout configuration.
        output_path: Destination DOCX path.
        sandbox: Whether to sandbox the Jinja environment.
        loader_dir: Optional loader root for {% extends %}.

    Returns:
        Path: The generated DOCX file path.
    """
    return render_docx(
        template_source, data, config, output_path, sandbox=sandbox, loader_dir=loader_dir
    )
