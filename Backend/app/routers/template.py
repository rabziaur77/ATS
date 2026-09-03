"""
Module: template.py
Created: 2026-09-03
Purpose: Template listing and custom template management with session scoping.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.template import Template
from app.routers import get_session_id
from app.schemas.template import (
    CustomTemplateCreate,
    CustomTemplateOut,
    CustomTemplateUpdate,
    TemplateListOut,
    TemplateOut,
)
from app.services.template_service import template_service
from app.utils.exceptions import NotFoundError, ScopingViolation

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.get("", response_model=TemplateListOut)
async def list_templates(
    session: AsyncSession = Depends(get_session),
    session_id: str = Depends(get_session_id),
) -> dict:
    """List all built-in and the caller's custom templates.

    Args:
        session: Database session.
        session_id: Caller's session id.

    Returns:
        dict: {"count", "items"} for the combined template list.
    """
    builtin = template_service.list_builtin()
    custom_rows = (
        await session.execute(
            select(Template).where(
                Template.is_custom.is_(True), Template.session_id == session_id
            )
        )
    ).scalars().all()
    custom_items = [
        TemplateOut(id=str(t.id), name=t.name, is_custom=True).model_dump()
        for t in custom_rows
    ]
    items = [TemplateOut(**b).model_dump() for b in builtin] + custom_items
    return {"count": len(items), "items": items}


@router.post("/custom", response_model=CustomTemplateOut, status_code=201)
async def create_custom_template(
    payload: CustomTemplateCreate,
    session: AsyncSession = Depends(get_session),
    session_id: str = Depends(get_session_id),
) -> Template:
    """Create a new custom template (validated and sandboxed).

    Args:
        payload: Custom template details.
        session: Database session.
        session_id: Caller's session id.

    Returns:
        Template: The stored custom template.
    """
    if payload.html_template:
        template_service.validate_custom_html(payload.html_template)
    row = Template(
        session_id=session_id,
        name=payload.name,
        config=payload.config,
        html_template=payload.html_template,
        is_custom=True,
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


@router.put("/custom/{template_id}", response_model=CustomTemplateOut)
async def update_custom_template(
    template_id: int,
    payload: CustomTemplateUpdate,
    session: AsyncSession = Depends(get_session),
    session_id: str = Depends(get_session_id),
) -> Template:
    """Update an existing custom template.

    Args:
        template_id: Custom template id.
        payload: Fields to update.
        session: Database session.
        session_id: Caller's session id.

    Returns:
        Template: The updated custom template.
    """
    row = await _get_scoped_custom(session, session_id, template_id)
    if payload.name is not None:
        row.name = payload.name
    if payload.config is not None:
        row.config = payload.config
    if payload.html_template is not None:
        template_service.validate_custom_html(payload.html_template)
        row.html_template = payload.html_template
    await session.commit()
    await session.refresh(row)
    return row


@router.delete("/custom/{template_id}", status_code=204)
async def delete_custom_template(
    template_id: int,
    session: AsyncSession = Depends(get_session),
    session_id: str = Depends(get_session_id),
) -> None:
    """Delete a custom template.

    Args:
        template_id: Custom template id.
        session: Database session.
        session_id: Caller's session id.
    """
    row = await _get_scoped_custom(session, session_id, template_id)
    await session.delete(row)
    await session.commit()


@router.get("/{template_id}", response_model=dict)
async def get_template(
    template_id: str,
    session: AsyncSession = Depends(get_session),
    session_id: str = Depends(get_session_id),
) -> dict:
    """Fetch a template's metadata and layout config.

    Args:
        template_id: Builtin name or custom template id.
        session: Database session.
        session_id: Caller's session id.

    Returns:
        dict: Template details (id, config, preview hint).

    Raises:
        NotFoundError / ScopingViolation: If missing or out of scope.
    """
    resolved = await _resolve_for_session(session, session_id, template_id)
    return {
        "id": resolved["id"],
        "config": resolved["config"],
        "is_custom": resolved["is_custom"],
    }


async def _resolve_for_session(
    session: AsyncSession, session_id: str, template_id: str
) -> dict:
    """Resolve a template id within the session's allowed scope.

    Args:
        session: Database session.
        session_id: Caller's session id.
        template_id: Template identifier.

    Returns:
        dict: Resolved template (id, config, is_custom).
    """
    if template_id.isdigit():
        custom = await _get_scoped_custom(session, session_id, int(template_id))
        return {"id": str(custom.id), "config": custom.config, "is_custom": True}
    return {
        "id": template_id,
        "config": template_service.get_builtin_config(template_id),
        "is_custom": False,
    }


async def _get_scoped_custom(
    session: AsyncSession, session_id: str, template_id: int
) -> Template:
    """Fetch a custom template ensuring session scoping.

    Args:
        session: Database session.
        session_id: Caller's session id.
        template_id: Custom template id.

    Returns:
        Template: The matching custom template.

    Raises:
        NotFoundError / ScopingViolation: If missing or out of scope.
    """
    row = (
        await session.execute(
            select(Template).where(Template.id == template_id)
        )
    ).scalar_one_or_none()
    if row is None:
        raise NotFoundError(f"Custom template '{template_id}'")
    if row.session_id != session_id:
        raise ScopingViolation()
    return row
