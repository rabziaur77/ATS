"""
Module: main.py
Created: 2026-09-03
Purpose: FastAPI application entry point, CORS, lifespan, and error handling.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.routers import resume as resume_router
from app.routers import template as template_router
from app.routers import upload as upload_router
from app.utils.exceptions import AppError


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database on startup and clean up on shutdown.

    Args:
        app: The FastAPI application instance.
    """
    await init_db()
    yield
    from app.database import engine

    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="ATS backend: upload CVs, choose a template, generate a formatted resume.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router.router)
app.include_router(resume_router.router)
app.include_router(template_router.router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Convert application errors to a consistent JSON error shape.

    Args:
        request: The incoming request.
        exc: The raised application error.

    Returns:
        JSONResponse: Error payload {code, message}.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.get("/health")
async def health() -> dict:
    """Simple liveness endpoint.

    Returns:
        dict: Service status.
    """
    return {"status": "ok", "app": settings.app_name}
