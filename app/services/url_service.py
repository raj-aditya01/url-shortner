from __future__ import annotations

from app.repositories.url_repository import UrlRepository
from app.services.base62_encoder import Base62Encoder


class UrlShortenerService:
    """Service that handles URL shortening business logic.
    
    This class coordinates creating, retrieving, and tracking URLs.
    """

    def __init__(self, repository: UrlRepository) -> None:
        # Receives repository as dependency (passed in constructor)
        self._repository = repository

    def create_short_code(self, original_url: str) -> str:
        """Create and save a new short code for a URL.
        
        Args:
            original_url: The full URL to be shortened
            
        Returns:
            The short code (e.g., 'abc123')
        """
        url_id = self._repository.save_and_get_id(original_url)
        short_hash = Base62Encoder.encode(url_id)
        self._repository.update_short_hash(url_id, short_hash, original_url)
        return short_hash

    def resolve_url(self, short_hash: str) -> str | None:
        """Look up the original URL for a given short code.
        
        Args:
            short_hash: The short code (e.g., 'abc123')
            
        Returns:
            The original URL, or None if not found
        """
        return self._repository.get_original_url(short_hash)

    def track_click(self, short_hash: str) -> None:
        """Increase the click count for a short code.
        
        Args:
            short_hash: The short code being clicked
        """
        self._repository.increment_click_count(short_hash)
