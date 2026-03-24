# ============================================================================
# MAIN.PY - APPLICATION ENTRY POINT
# ============================================================================
# This file is where the FastAPI application is created and configured.
# It's the first file that runs when you start the server with uvicorn.
#
# Think of this as the "front door" to your application.
# ============================================================================

# IMPORTS: Bringing in code from other files/libraries
# ----------------------------------------------------------------------------
# FastAPI: The web framework that handles HTTP requests and responses
from fastapi import FastAPI

# Router: Contains all our URL endpoints (routes) like /shorten, /{code}, etc.
from app.api.routes.url_routes import router as url_router

# Logging setup: Configures how we write debug/info messages
from app.core.logging_config import setup_logging

# These sqlite3 imports are not used here but kept for reference
from sqlite3 import Connection, connect


# ============================================================================
# FUNCTION: create_app
# ============================================================================
# This is a FACTORY FUNCTION - it creates and returns a new FastAPI app instance
# 
# WHY USE A FACTORY FUNCTION?
# - Makes testing easier (each test can create a fresh app)
# - Allows creating multiple app instances if needed
# - Separates app creation logic from the actual app instance
# - Follows the "Factory Pattern" in OOP
#
# RETURN TYPE: FastAPI
# - The -> FastAPI tells Python what type of object this function returns
# - This helps with code completion and catching errors early
# ============================================================================
def create_app() -> FastAPI:
    """Create and configure the FastAPI application.
    
    This function:
    1. Sets up logging so we can see what's happening
    2. Creates a new FastAPI application instance
    3. Registers all URL routes (endpoints) from url_router
    4. Returns the configured application
    
    Returns:
        FastAPI: A fully configured FastAPI application ready to handle requests
        
    Example:
        app = create_app()  # Creates the application
        # Now you can run: uvicorn app.main:app --reload
    """
    
    # STEP 1: Configure logging
    # This sets up how the app writes messages to the console
    # After this, you can use logger.info("message") anywhere in the app
    setup_logging()
    
    # STEP 2: Create the FastAPI application instance
    # FastAPI() is a CONSTRUCTOR call - it creates a new object of class FastAPI
    # The 'title' parameter sets the API title shown in documentation
    application = FastAPI(title="URL Shortener API")
    
    # STEP 3: Register all routes from url_router
    # include_router() is a METHOD call on the application object
    # This adds all the endpoints defined in url_routes.py to our app
    # After this, endpoints like POST /shorten and GET /{short_hash} work
    application.include_router(url_router)
    
    # STEP 4: Return the configured app
    # This app object will handle all incoming HTTP requests
    return application


# ============================================================================
# CREATE THE APP INSTANCE
# ============================================================================
# This line runs when the file is imported (when uvicorn loads it)
# It calls create_app() and stores the result in the variable 'app'
#
# When you run: uvicorn app.main:app --reload
# - uvicorn looks for the file 'app/main.py'
# - It finds the variable named 'app'
# - It uses that FastAPI instance to handle HTTP requests
# ============================================================================
app = create_app()