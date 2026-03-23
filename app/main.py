from fastapi import FastAPI

from app.api.routes.url_routes import router as url_router
from app.core.logging_config import setup_logging
from sqlite3 import Connection, connect


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    Sets up logging and adds the URL shortener routes.
    This pattern allows the app to be created multiple times for testing.
    """
    setup_logging()
    application = FastAPI(title="URL Shortener API")
    # Add all URL shortener routes (POST /shorten, GET /{code}, etc.)
    application.include_router(url_router)
    return application


app = create_app()