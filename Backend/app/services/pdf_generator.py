"""
Module: pdf_generator.py
Created: 2026-09-03
Purpose: Thin wrapper emitting PDF resumes via the shared render engine.
"""

from pathlib import Path

from app.services.html_generator import render_pdf


def generate_pdf(
    template_source: str,
    data: dict,
    config: dict,
    output_path: Path,
    sandbox: bool = True,
    loader_dir: str | None = None,
) -> Path:
    """Generate a PDF resume.

    Args:
        template_source: Jinja2 HTML template source.
        data: Template-ready resume data.
        config: Template layout configuration.
        output_path: Destination PDF path.
        sandbox: Whether to sandbox the Jinja environment.
        loader_dir: Optional loader root for {% extends %}.

    Returns:
        Path: The generated PDF file path.
    """
    return render_pdf(
        template_source, data, config, output_path, sandbox=sandbox, loader_dir=loader_dir
    )
