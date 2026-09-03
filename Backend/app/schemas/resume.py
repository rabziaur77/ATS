"""
Module: resume.py
Created: 2026-09-03
Purpose: Pydantic schemas for resume data (request/response) and generation.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PersonalInfo(BaseModel):
    """Contact and identification details extracted from a CV."""

    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    website: str = ""


class ExperienceItem(BaseModel):
    """A single work experience entry."""

    company: str = ""
    title: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""


class EducationItem(BaseModel):
    """A single education entry."""

    institution: str = ""
    degree: str = ""
    start_date: str = ""
    end_date: str = ""
    gpa: str = ""


class ParsedResumeData(BaseModel):
    """The full structured representation of a parsed CV."""

    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    summary: str = ""
    experience: list[ExperienceItem] = Field(default_factory=list)
    education: list[EducationItem] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    projects: list[dict] = Field(default_factory=list)


class ResumeCreate(BaseModel):
    """Payload for creating/updating resume structured data."""

    parsed_data: ParsedResumeData


class ResumeUpdate(BaseModel):
    """Payload for editing parsed resume data."""

    parsed_data: ParsedResumeData


class ResumeOut(BaseModel):
    """Read model returned for an uploaded resume."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    session_id: str
    filename: str
    file_type: str
    created_at: datetime
    updated_at: datetime


class ResumeDetailOut(ResumeOut):
    """Resume output including its parsed data."""

    parsed_data: dict


class GenerateRequest(BaseModel):
    """Request body for resume generation."""

    template_id: str
    format: str = "pdf"  # pdf | docx | html
    parsed_data: Optional[ParsedResumeData] = None


class GenerateResponse(BaseModel):
    """Response indicating a generated resume file."""

    id: int
    resume_id: int
    template_id: str
    format: str
    file_path: str
    created_at: datetime
