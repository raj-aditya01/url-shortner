from __future__ import annotations

import os
from pathlib import Path

from app.repositories.url_repository import SQLiteUrlRepository, UrlRepository
from app.services.url_service import UrlShortenerService

# Create single instances of repository and service to reuse across requests
_project_root = Path(__file__).parent.parent
_db_path = Path(os.getenv("SQLITE_DB_PATH", str(_project_root / "data" / "url_shortener.db"))).resolve()
_db_path.parent.mkdir(parents=True, exist_ok=True)

_repository = SQLiteUrlRepository(str(_db_path))
_service = UrlShortenerService(_repository)


def get_db() -> UrlRepository:
    """Get the database repository instance for dependency injection."""
    return _repository


def get_url_service() -> UrlShortenerService:
    """Get the URL shortener service instance for dependency injection."""
    return _service
