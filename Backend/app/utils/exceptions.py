"""
Module: exceptions.py
Created: 2026-09-03
Purpose: Central application exception types for consistent error handling.
"""


class AppError(Exception):
    """Base class for all application-level errors."""

    status_code = 400
    code = "app_error"

    def __init__(self, message: str = "", *, status_code: int | None = None, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        if code is not None:
            self.code = code


class UnsupportedFileType(AppError):
    """Raised when a file is uploaded with an unsupported extension."""

    def __init__(self, file_type: str) -> None:
        super().__init__(
            f"Unsupported file type: {file_type}. Allowed: pdf, docx, txt.",
            code="unsupported_file_type",
        )


class FileTooLarge(AppError):
    """Raised when an upload exceeds the configured size limit."""

    def __init__(self, limit_mb: int) -> None:
        super().__init__(
            f"File exceeds the maximum size of {limit_mb} MB.",
            status_code=413,
            code="file_too_large",
        )


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    def __init__(self, resource: str = "Resource") -> None:
        super().__init__(f"{resource} not found.", status_code=404, code="not_found")


class ScopingViolation(AppError):
    """Raised when a request tries to access a resource outside its scope."""

    def __init__(self) -> None:
        super().__init__(
            "Access to the requested resource is not allowed for this session.",
            status_code=404,
            code="scoping_violation",
        )


class ParsingError(AppError):
    """Raised when a CV cannot be parsed into structured data."""

    def __init__(self, detail: str = "Could not parse CV content.") -> None:
        super().__init__(detail, status_code=422, code="parsing_error")


class TemplateRenderError(AppError):
    """Raised when a template cannot be rendered."""

    def __init__(self, detail: str = "Could not render template.") -> None:
        super().__init__(detail, status_code=422, code="template_render_error")
