"""
Module: template.py
Created: 2026-09-03
Purpose: Pydantic schemas for template listing and custom templates.
"""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class TemplateOut(BaseModel):
    """Public metadata for a single template (built-in or custom)."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    style: Optional[str] = None
    is_custom: bool = False


class TemplateListOut(BaseModel):
    """A list of templates plus a count."""

    count: int
    items: list[TemplateOut]


class TemplateDetailOut(TemplateOut):
    """Template detail including its layout config."""

    config: dict = Field(default_factory=dict)


class CustomTemplateCreate(BaseModel):
    """Payload to create a custom user template."""

    name: str
    config: dict = Field(default_factory=dict)
    html_template: str = ""


class CustomTemplateUpdate(BaseModel):
    """Payload to update an existing custom template."""

    name: Optional[str] = None
    config: Optional[dict] = None
    html_template: Optional[str] = None


class CustomTemplateOut(BaseModel):
    """Read model for a custom template."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    name: str
    config: dict
    html_template: str
    is_custom: bool
