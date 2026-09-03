"""
Module: upload.py
Created: 2026-09-03
Purpose: Endpoint to upload a CV and receive parsed structured data.
"""

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_session
from app.models.resume import Resume
from app.routers import get_session_id
from app.schemas.resume import ResumeDetailOut
from app.services.cv_parser import parse_cv
from app.utils.exceptions import FileTooLarge, UnsupportedFileType

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/cv", response_model=ResumeDetailOut, status_code=201)
async def upload_cv(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    session_id: str = Depends(get_session_id),
) -> Resume:
    """Accept a CV upload, validate it, parse it, and store the result.

    The parsing is CPU/IO-bound, so it is offloaded to a worker thread to avoid
    blocking the event loop.

    Args:
        file: The uploaded CV file (pdf/docx/txt).
        session: Database session.
        session_id: Caller's session id (scoping).

    Returns:
        Resume: The stored resume with parsed_data populated.

    Raises:
        UnsupportedFileType: If the extension is not allowed.
        FileTooLarge: If the file exceeds the size limit.
    """
    ext = _extension(file.filename)
    _validate_extension(ext)

    content = await file.read()
    if len(content) > settings.max_upload_size_mb * 1024 * 1024:
        raise FileTooLarge(settings.max_upload_size_mb)

    import asyncio

    parsed = await asyncio.to_thread(parse_cv, content, ext)

    rel_path = _store_upload(content, ext)

    resume = Resume(
        session_id=session_id,
        filename=file.filename or "resume",
        file_path=str(rel_path),
        file_type=ext,
        parsed_data=parsed.model_dump(),
    )
    session.add(resume)
    await session.commit()
    await session.refresh(resume)
    return resume


def _extension(filename: str | None) -> str:
    """Return the lowercase extension of a filename without the dot.

    Args:
        filename: Original upload filename.

    Returns:
        str: Extension like 'pdf'.

    Raises:
        UnsupportedFileType: If there is no extension.
    """
    if not filename or "." not in filename:
        raise UnsupportedFileType("")
    return filename.rsplit(".", 1)[1].lower()


def _validate_extension(ext: str) -> None:
    """Raise if an extension is not in the allowed set.

    Args:
        ext: Lowercase extension.

    Raises:
        UnsupportedFileType: If the extension is not allowed.
    """
    if f".{ext}" not in settings.allowed_extensions:
        raise UnsupportedFileType(ext)


def _store_upload(content: bytes, ext: str) -> Path:
    """Persist uploaded bytes into the uploads directory.

    Args:
        content: Raw file bytes.
        ext: File extension.

    Returns:
        Path: Relative path under settings.upload_dir.
    """
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    rel = Path(f"{uuid4().hex}.{ext}")
    (settings.upload_dir / rel).write_bytes(content)
    return rel
