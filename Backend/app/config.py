"""
Module: config.py
Created: 2026-09-03
Purpose: Application settings loaded from environment variables / defaults.
         Central place for paths, limits, and optional AI config.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """App settings sourced from env vars (with sensible defaults)."""

    app_name: str = "ATS Backend"
    debug: bool = True

    upload_dir: Path = BASE_DIR / "uploads"
    output_dir: Path = BASE_DIR / "outputs"
    templates_dir: Path = BASE_DIR / "app" / "templates"

    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR / 'ats.db'}"

    max_upload_size_mb: int = 10
    allowed_extensions: tuple[str, str, str] = (".pdf", ".docx", ".txt")

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = Settings()
