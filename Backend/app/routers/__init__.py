"""
Module: routers/__init__.py
Created: 2026-09-03
Purpose: Bundle route modules and shared routing dependencies.
"""

from fastapi import Cookie, Header

SESSION_HEADER = "x-session-id"
SESSION_COOKIE = "ats_session_id"


async def get_session_id(
    x_session_id: str = Header(default=None),
    ats_session_id: str = Cookie(default=None),
) -> str:
    """Extract the session id from the request header or cookie.

    Falls back to the ``ats_session_id`` cookie when the header is absent,
    which allows iframe browser requests (that cannot carry custom headers)
    to authenticate correctly.

    Args:
        x_session_id: Session identifier header value.
        ats_session_id: Session identifier cookie value.

    Returns:
        str: The normalized session id, or "anonymous" when neither source
             provides a value.
    """
    raw = x_session_id or ats_session_id
    return (raw or "anonymous").strip()[:64]


__all__ = ["get_session_id", "SESSION_HEADER", "SESSION_COOKIE"]
