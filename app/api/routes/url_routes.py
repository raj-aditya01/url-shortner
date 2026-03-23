import logging
import os

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import RedirectResponse

from app.dependencies import get_db, get_url_service
from app.models.schemas import URLCreateRequest, URLCreateResponse
from app.repositories.url_repository import UrlRepository
from app.services.url_service import UrlShortenerService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["URL Shortener"])
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")


@router.post("/shorten", response_model=URLCreateResponse)
async def create_short_url(
    request: URLCreateRequest,
    service: UrlShortenerService = Depends(get_url_service),
) -> URLCreateResponse:
    """Create a short URL from a long URL.
    
    Takes a URL in the request body and returns a short code.
    Example: https://example.com/very/long/url -> http://127.0.0.1:8000/abc123
    """
    short_hash = service.create_short_code(str(request.original_url))
    logger.info("Created short URL %s for %s", short_hash, request.original_url)
    return URLCreateResponse(
        short_url=f"{BASE_URL}/{short_hash}",
        original_url=str(request.original_url),
    )


@router.get("/{short_hash}")
async def redirect_to_original(
    short_hash: str,
    background_tasks: BackgroundTasks,
    service: UrlShortenerService = Depends(get_url_service),
):
    """Redirect from short URL to original URL.
    
    Example: GET /abc123 -> redirects to https://example.com/very/long/url
    Also tracks the click in the background (doesn't slow down the redirect).
    """
    original_url = service.resolve_url(short_hash)
    if not original_url:
        logger.warning("Short hash not found: %s", short_hash)
        raise HTTPException(status_code=404, detail="Short URL not found in database")

    # Update click count in background (doesn't delay the redirect response)
    background_tasks.add_task(service.track_click, short_hash)
    logger.info("Redirecting %s to %s", short_hash, original_url)
    return RedirectResponse(url=original_url, status_code=302)


@router.get("/admin/database")
async def view_database(db: UrlRepository = Depends(get_db)):
    """Admin endpoint: View all stored URLs and their statistics.
    
    Returns the number of stored URLs and their full details.
    WARNING: This endpoint has no authentication - do not expose in production!
    """
    snapshot = db.get_all()
    return {
        "total_urls_stored": len(snapshot),
        "database_contents": snapshot,
    }