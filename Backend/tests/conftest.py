"""
Module: conftest.py
Created: 2026-09-03
Purpose: Shared pytest fixtures and global configuration.
"""

import os
import tempfile
from pathlib import Path

import pytest

# Isolate config before importing the app so tests do not touch real dirs.
_test_tmp = Path(tempfile.mkdtemp(prefix="ats_test_"))
os.environ["UPLOAD_DIR"] = str(_test_tmp / "uploads")
os.environ["OUTPUT_DIR"] = str(_test_tmp / "outputs")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_test_tmp / 'test.db'}"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Provide a TestClient bound to the app with a clean test DB."""
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def sample_cv_bytes() -> bytes:
    """Return the sample CV as raw bytes for uploads."""
    return (FIXTURES / "sample_cv.txt").read_bytes()
