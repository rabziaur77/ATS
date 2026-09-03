"""
Module: template_service.py
Created: 2026-09-03
Purpose: Resolves built-in (filesystem) and custom (database) templates,
         validates custom template content, and lists available templates.
"""

import json
import re
from pathlib import Path
from typing import Optional

from jinja2.sandbox import SandboxedEnvironment

from app.config import settings
from app.models.template import Template
from app.utils.exceptions import NotFoundError, TemplateRenderError

TEMPLATE_CONFIG_FILENAME = "config.json"
TEMPLATE_HTML_FILENAME = "template.html"

BUILTIN_STYLES = {
    "classic": "Traditional reverse-chronological, serif fonts",
    "modern": "Clean lines, sans-serif, colored accents",
    "minimal": "Whitespace-focused, minimal decoration",
    "executive": "Formal, sophisticated, for senior roles",
    "technical": "Skills-forward, project-centric layout",
    "professional": "Balanced, corporate-friendly",
    "academic": "Research/publications focus, detailed",
    "simple": "Bare-bones, maximum ATS readability",
    "elegant": "Subtle typography, refined spacing",
    "ats_standard": "Optimized for ATS parsing, clean sections",
}


class TemplateService:
    """Resolves and validates resume templates."""

    def __init__(self) -> None:
        self.builtin_root = settings.templates_dir

    def list_builtin(self) -> list[dict]:
        """List all built-in filesystem templates.

        Returns:
            list[dict]: Metadata ({id, name, style, is_custom}) for each.
        """
        result: list[dict] = []
        if not self.builtin_root.exists():
            return result
        for folder in sorted(self.builtin_root.iterdir()):
            if folder.is_dir() and self._is_valid_builtin(folder):
                result.append(self._builtin_meta(folder.name))
        return result

    def _is_valid_builtin(self, folder: Path) -> bool:
        return (folder / TEMPLATE_CONFIG_FILENAME).exists()

    def _builtin_meta(self, template_id: str) -> dict:
        return {
            "id": template_id,
            "name": template_id.replace("_", " ").title(),
            "style": BUILTIN_STYLES.get(template_id, ""),
            "layout": self._builtin_layout(template_id),
            "is_custom": False,
        }

    def _builtin_layout(self, template_id: str) -> str:
        """Return the structural layout label for a built-in template.

        Falls back to "single_column" when a config file is missing or lacks
        a layout field, so listing never breaks on malformed configs.

        Args:
            template_id: Name of the built-in template folder.

        Returns:
            str: The template's layout label.
        """
        try:
            return str(self.get_builtin_config(template_id).get("layout", "single_column"))
        except NotFoundError:
            return "single_column"

    def get_builtin_config(self, template_id: str) -> dict:
        """Load the layout config JSON for a built-in template.

        Args:
            template_id: Name of the built-in template folder.

        Returns:
            dict: The template's layout configuration.

        Raises:
            NotFoundError: If the template folder or config is missing.
        """
        config_path = self.builtin_root / template_id / TEMPLATE_CONFIG_FILENAME
        if not config_path.exists():
            raise NotFoundError(f"Template '{template_id}'")
        try:
            return json.loads(config_path.read_text(encoding="utf-8-sig").strip("\ufeff"))
        except (json.JSONDecodeError, OSError) as exc:
            raise TemplateRenderError(f"Invalid config for template '{template_id}'") from exc

    def get_builtin_html(self, template_id: str) -> str:
        """Load the Jinja2 HTML template content for a built-in template.

        Args:
            template_id: Name of the built-in template folder.

        Returns:
            str: The raw HTML template source.

        Raises:
            NotFoundError: If the HTML file is missing.
        """
        html_path = self.builtin_root / template_id / TEMPLATE_HTML_FILENAME
        if not html_path.exists():
            raise NotFoundError(f"Template HTML for '{template_id}'")
        return html_path.read_text(encoding="utf-8-sig").lstrip("\ufeff")

    def validate_custom_html(self, html_source: str) -> None:
        """Validate that a custom template compiles in a sandboxed env.

        Args:
            html_source: The user-supplied Jinja2 HTML source.

        Raises:
            TemplateRenderError: If the source fails to compile or is unsafe.
        """
        if self._looks_unsafe(html_source):
            raise TemplateRenderError(
                "Custom template uses forbidden expressions. "
                "Only attribute access and basic filters are allowed."
            )
        env = SandboxedEnvironment()
        try:
            env.from_string(html_source)
        except Exception as exc:
            raise TemplateRenderError(f"Invalid template syntax: {exc}") from exc

    def _looks_unsafe(self, source: str) -> bool:
        """Heuristically reject templates attempting sandbox escape.

        Args:
            source: Jinja2 template source text.

        Returns:
            bool: True if the source is likely unsafe.
        """
        forbidden = ("__class__", "__globals__", "__mro__", "__subclasses__",
                     "cycler", "joiner", "namespace", "url_for", "getattr",
                     "range", "dict", "lipsum")
        return any(f in source for f in forbidden)

    def resolve(self, template_id: str, session_id: str, db_custom: list[Template]) -> dict:
        """Resolve a template by id, preferring custom DB templates.

        Args:
            template_id: The template identifier (builtin name or custom 'id').
            session_id: The requesting session (ignored for builtins).
            db_custom: Custom templates already scoped to this session.

        Returns:
            dict: {"id", "html", "config", "is_custom"}.

        Raises:
            NotFoundError: If neither a builtin nor a matching custom exists.
        """
        custom = next(
            (t for t in db_custom if str(t.id) == str(template_id)), None
        )
        if custom is not None:
            return {
                "id": str(custom.id),
                "html": custom.html_template,
                "config": custom.config,
                "layout": custom.config.get("layout", "custom"),
                "is_custom": True,
            }

        if (self.builtin_root / template_id).is_dir():
            config = self.get_builtin_config(template_id)
            return {
                "id": template_id,
                "html": self.get_builtin_html(template_id),
                "config": config,
                "layout": config.get("layout", "single_column"),
                "is_custom": False,
            }

        raise NotFoundError(f"Template '{template_id}'")


template_service = TemplateService()
