"""
Module: routers/__init__.py
Created: 2026-09-03
Purpose: Bundle route modules and shared routing dependencies.
"""

from fastapi import Header

SESSION_HEADER = "x-session-id"


async def get_session_id(
    x_session_id: str = Header(default="anonymous"),
) -> str:
    """Extract the session id from the request header.

    Args:
        x_session_id: Session identifier header value.

    Returns:
        str: The normalized session id.
    """
    return (x_session_id or "anonymous").strip()[:64]


__all__ = ["get_session_id", "SESSION_HEADER"]
