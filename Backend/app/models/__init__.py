"""
Module: models/__init__.py
Created: 2026-09-03
Purpose: Bundle all ORM models for easy import and metadata registration.
"""

from app.models.resume import GeneratedResume, Resume
from app.models.template import Template

__all__ = ["Resume", "GeneratedResume", "Template"]
