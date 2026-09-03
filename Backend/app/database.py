"""
Module: database.py
Created: 2026-09-03
Purpose: SQLAlchemy async engine, session factory, and declarative Base.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


engine = create_async_engine(settings.database_url, echo=settings.debug, future=True)

async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session():
    """Provide an async session dependency for route handlers.

    Yields:
        AsyncSession: An open database session, closed after the request.
    """
    async with async_session_factory() as session:
        yield session


async def init_db() -> None:
    """Create all tables referenced by the models metadata."""
    from app import models  # noqa: F401 - import to register models

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
