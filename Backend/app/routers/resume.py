"""
Module: resume.py
Created: 2026-09-03
Purpose: Resume CRUD, generation, preview, and download endpoints with
         session-based scoping enforced on every query.
"""

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session
from app.models.resume import GeneratedResume, Resume
from app.models.template import Template
from app.routers import get_session_id
from app.schemas.resume import (
    GenerateRequest,
    GenerateResponse,
    ParsedResumeData,
    ResumeDetailOut,
    ResumeOut,
    ResumeUpdate,
)
from app.services import resume_processor
from app.services.docx_generator import generate_docx
from app.services.html_generator import render_html
from app.services.pdf_generator import generate_pdf
from app.services.template_service import template_service
from app.utils.exceptions import NotFoundError, ScopingViolation

router = APIRouter(prefix="/api/resume", tags=["resume"])


@router.get("/list", response_model=list[ResumeOut])
async def list_resumes(
    session: AsyncSession = Depends(get_session),
    session_id: str = Depends(get_session_id),
) -> list[Resume]:
    """List resumes scoped to the caller's session.

    Args:
        session: Database session.
        session_id: Caller's session id.

    Returns:
        list[Resume]: Resumes owned by the session, newest first.
    """
    result = await session.execute(
        select(Resume)
        .where(Resume.session_id == session_id)
        .order_by(Resume.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{resume_id}", response_model=ResumeDetailOut)
async def get_resume(
    resume_id: int,
    session: AsyncSession = Depends(get_session),
    session_id: str = Depends(get_session_id),
) -> Resume:
    """Get a single resume with its parsed data.

    Args:
        resume_id: Resume id.
        session: Database session.
        session_id: Caller's session id.

    Returns:
        Resume: The resume record.

    Raises:
        NotFoundError / ScopingViolation: If missing or out of scope.
    """
    return await _get_scoped_resume(session, session_id, resume_id)


@router.put("/{resume_id}", response_model=ResumeDetailOut)
async def update_resume(
    resume_id: int,
    payload: ResumeUpdate,
    session: AsyncSession = Depends(get_session),
    session_id: str = Depends(get_session_id),
) -> Resume:
    """Update the parsed data of a resume.

    Args:
        resume_id: Resume id.
        payload: New parsed data.
        session: Database session.
        session_id: Caller's session id.

    Returns:
        Resume: The updated resume.
    """
    resume = await _get_scoped_resume(session, session_id, resume_id)
    resume.parsed_data = payload.parsed_data.model_dump()
    await session.commit()
    await session.refresh(resume)
    return resume


@router.delete("/{resume_id}", status_code=204)
async def delete_resume(
    resume_id: int,
    session: AsyncSession = Depends(get_session),
    session_id: str = Depends(get_session_id),
) -> None:
    """Delete a resume and its on-disk upload.

    Args:
        resume_id: Resume id.
        session: Database session.
        session_id: Caller's session id.
    """
    resume = await _get_scoped_resume(session, session_id, resume_id)
    await session.delete(resume)
    await session.commit()


@router.post("/{resume_id}/generate", response_model=GenerateResponse, status_code=201)
async def generate_resume(
    resume_id: int,
    payload: GenerateRequest,
    session: AsyncSession = Depends(get_session),
    session_id: str = Depends(get_session_id),
) -> GeneratedResume:
    """Generate a formatted resume (pdf/docx/html) from a resume.

    Generation is CPU/IO-bound, so it runs in a worker thread.

    Args:
        resume_id: Resume id.
        payload: Template and format selection.
        session: Database session.
        session_id: Caller's session id.

    Returns:
        GeneratedResume: The stored generated output record.
    """
    resume = await _get_scoped_resume(session, session_id, resume_id)
    parsed = payload.parsed_data
    if parsed is None:
        parsed = ParsedResumeData.model_validate(resume.parsed_data)

    fmt = payload.format.lower()
    if fmt not in ("pdf", "docx", "html"):
        raise HTTPException(status_code=422, detail="format must be pdf, docx, or html")

    custom = await _custom_templates(session, session_id)
    resolved = template_service.resolve(payload.template_id, session_id, custom)
    data = resume_processor.process(parsed, resolved["config"])
    loader_dir = str(settings.templates_dir)

    output_name = f"{resume.id}_{payload.template_id}_{uuid_hex()}.{fmt}"
    output_path = settings.output_dir / output_name
    settings.output_dir.mkdir(parents=True, exist_ok=True)

    import asyncio

    if fmt == "pdf":
        await asyncio.to_thread(
            generate_pdf, resolved["html"], data, resolved["config"], output_path,
            resolved["is_custom"], loader_dir,
        )
    elif fmt == "docx":
        await asyncio.to_thread(
            generate_docx, resolved["html"], data, resolved["config"], output_path,
            resolved["is_custom"], loader_dir,
        )
    else:
        html = await asyncio.to_thread(
            render_html, resolved["html"], data,
            sandbox=resolved["is_custom"], loader_dir=loader_dir,
        )
        output_path.write_text(html, encoding="utf-8")

    generated = GeneratedResume(
        resume_id=resume.id,
        template_id=payload.template_id,
        format=fmt,
        file_path=str(output_path),
    )
    session.add(generated)
    await session.commit()
    await session.refresh(generated)
    return generated


@router.get("/{resume_id}/preview", response_class=HTMLResponse)
async def preview_resume(
    resume_id: int,
    template_id: str = Query(..., description="Template id to preview"),
    session: AsyncSession = Depends(get_session),
    session_id: str = Depends(get_session_id),
) -> str:
    """Render a resume as HTML for browser preview.

    Args:
        resume_id: Resume id.
        template_id: Template to preview with.
        session: Database session.
        session_id: Caller's session id.

    Returns:
        str: Rendered HTML.
    """
    resume = await _get_scoped_resume(session, session_id, resume_id)
    parsed = ParsedResumeData.model_validate(resume.parsed_data)
    custom = await _custom_templates(session, session_id)
    resolved = template_service.resolve(template_id, session_id, custom)
    data = resume_processor.process(parsed, resolved["config"])
    loader_dir = str(settings.templates_dir)
    return render_html(
        resolved["html"], data, sandbox=resolved["is_custom"], loader_dir=loader_dir
    )


@router.get("/{resume_id}/download/{generated_id}")
async def download_resume(
    resume_id: int,
    generated_id: int,
    session: AsyncSession = Depends(get_session),
    session_id: str = Depends(get_session_id),
) -> FileResponse:
    """Download a previously generated resume file.

    Args:
        resume_id: Resume id.
        generated_id: Generated output record id.
        session: Database session.
        session_id: Caller's session id.

    Returns:
        FileResponse: The generated file.

    Raises:
        HTTPException: If the path is outside the outputs directory.
    """
    resume = await _get_scoped_resume(session, session_id, resume_id)
    generated = (
        await session.execute(
            select(GeneratedResume).where(
                GeneratedResume.id == generated_id,
                GeneratedResume.resume_id == resume.id,
            )
        )
    ).scalar_one_or_none()
    if generated is None:
        raise NotFoundError(f"Generated resume '{generated_id}'")

    path = Path(generated.file_path).resolve()
    if not str(path).startswith(str(settings.output_dir.resolve())):
        raise HTTPException(status_code=400, detail="Invalid file path")
    if not path.exists():
        raise NotFoundError("Generated resume file")
    return FileResponse(str(path))


async def _get_scoped_resume(
    session: AsyncSession, session_id: str, resume_id: int
) -> Resume:
    """Fetch a resume ensuring session scoping.

    Args:
        session: Database session.
        session_id: Caller's session id.
        resume_id: Resume id.

    Returns:
        Resume: The matching resume.

    Raises:
        ScopingViolation: If the resume does not belong to this session.
    """
    resume = (
        await session.execute(
            select(Resume).where(Resume.id == resume_id)
        )
    ).scalar_one_or_none()
    if resume is None:
        raise NotFoundError(f"Resume '{resume_id}'")
    if resume.session_id != session_id:
        raise ScopingViolation()
    return resume


async def _custom_templates(session: AsyncSession, session_id: str) -> list[Template]:
    """Fetch custom templates scoped to the session.

    Args:
        session: Database session.
        session_id: Caller's session id.

    Returns:
        list[Template]: Custom templates owned by the session.
    """
    result = await session.execute(
        select(Template).where(
            Template.is_custom.is_(True), Template.session_id == session_id
        )
    )
    return list(result.scalars().all())


def uuid_hex() -> str:
    """Return a short unique hex suffix for output filenames.

    Returns:
        str: 8-character hex string.
    """
    from uuid import uuid4

    return uuid4().hex[:8]
