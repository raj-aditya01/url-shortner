from pydantic import BaseModel, HttpUrl


class URLCreateRequest(BaseModel):
    """Request model: URL to be shortened."""
    original_url: HttpUrl


class URLCreateResponse(BaseModel):
    """Response model: Created short URL and original URL."""
    short_url: str
    original_url: str
