# ============================================================================
# URL_ROUTES.PY - API ROUTES / ENDPOINTS (PRESENTATION LAYER)
# ============================================================================
# This file defines the HTTP API endpoints (routes) for the URL shortener.
#
# WHAT IS A ROUTE/ENDPOINT?
# - A URL path that the API responds to (like /shorten or /abc123)
# - Maps HTTP requests to Python functions
# - The "front door" of your application - where users interact
#
# WHY SEPARATE ROUTES FROM BUSINESS LOGIC?
# - SEPARATION OF CONCERNS: HTTP handling vs business logic
# - TESTABILITY: Can test business logic without HTTP
# - REUSABILITY: Same service can be used by API, CLI, background jobs
# - MAINTAINABILITY: Changes to HTTP don't affect business logic
#
# ARCHITECTURE LAYERS:
# ┌────────────────────────┐
# │  Browser / HTTP Client │  ← User sends HTTP requests
# └──────────┬─────────────┘
#            ↓
# ┌──────────▼─────────────┐
# │  API Routes (this file)│  ← Handles HTTP, validates input, returns responses
# └──────────┬─────────────┘
#            ↓
# ┌──────────▼─────────────┐
# │  Service Layer         │  ← Business logic
# └──────────┬─────────────┘
#            ↓
# ┌──────────▼─────────────┐
# │  Repository Layer      │  ← Database operations
# └────────────────────────┘
# ============================================================================

# IMPORTS
# ----------------------------------------------------------------------------
# logging: Python's built-in logging library
import logging

# os: Access environment variables
import os

# FastAPI imports:
# - APIRouter: Groups related routes together
# - BackgroundTasks: Runs tasks after response is sent (non-blocking)
# - Depends: Dependency injection system
# - HTTPException: Raises HTTP errors (404, 500, etc.)
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

# RedirectResponse: Special response that redirects browser to another URL
from fastapi.responses import RedirectResponse

# Our dependency provider functions
from app.dependencies import get_db, get_url_service

# Our data models (request/response schemas)
from app.models.schemas import URLCreateRequest, URLCreateResponse

# Type hints for dependency injection
from app.repositories.url_repository import UrlRepository
from app.services.url_service import UrlShortenerService


# ============================================================================
# MODULE-LEVEL CONFIGURATION
# ============================================================================
# These variables are created once when the module is imported
# ============================================================================

# LOGGER: For writing log messages (info, warnings, errors)
# __name__ is the module name: "app.api.routes.url_routes"
# This allows filtering logs by module in production
logger = logging.getLogger(__name__)

# ROUTER: Groups all URL shortener routes together
# APIRouter() creates a new router instance
# tags=["URL Shortener"] adds metadata for API documentation
# All routes registered with this router will be tagged "URL Shortener"
# This helps organize the API docs (Swagger UI shows tags as sections)
router = APIRouter(tags=["URL Shortener"])

# BASE_URL: The base URL for generated short URLs
# os.getenv("BASE_URL", "default") reads an environment variable
# If BASE_URL env var is not set, uses "http://127.0.0.1:8000" as default
# This allows deployment flexibility:
# - Development: http://127.0.0.1:8000
# - Production: https://short.example.com
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")


# ============================================================================
# ROUTE: POST /shorten - Create a short URL
# ============================================================================
# This endpoint receives a long URL and returns a short URL.
#
# HTTP METHOD: POST
# - Used for creating new resources
# - Request body contains the data (original_url)
# - Returns the created resource (short_url)
#
# DECORATORS EXPLAINED:
# @router.post(...) registers this function as a POST endpoint
# - "/shorten": The URL path (http://127.0.0.1:8000/shorten)
# - response_model=URLCreateResponse: Tells FastAPI the response structure
#   * FastAPI will validate the response matches this model
#   * API docs will show the response schema
#   * Automatic JSON serialization
# ============================================================================
@router.post("/shorten", response_model=URLCreateResponse)
async def create_short_url(
    request: URLCreateRequest,
    service: UrlShortenerService = Depends(get_url_service),
) -> URLCreateResponse:
    """
    Create a short URL from a long URL.
    
    This endpoint is the main feature of the URL shortener.
    It receives a long URL and returns a shortened version.
    
    HTTP Request:
        Method: POST
        Path: /shorten
        Headers: Content-Type: application/json
        Body: {"original_url": "https://www.example.com/very/long/path"}
        
    HTTP Response:
        Status: 200 OK
        Body: {
            "short_url": "http://127.0.0.1:8000/abc123",
            "original_url": "https://www.example.com/very/long/path"
        }
    
    Args:
        request: The validated request data (URLCreateRequest model)
                FastAPI automatically:
                - Reads JSON from request body
                - Validates it matches URLCreateRequest schema
                - Creates a URLCreateRequest object
                - Passes it to this function
                
        service: The URL shortener service (DEPENDENCY INJECTION)
                FastAPI automatically:
                - Calls get_url_service() from dependencies.py
                - Injects the returned service instance
                - This is the Depends(...) magic!
                
    Returns:
        URLCreateResponse: Object containing short_url and original_url
                          FastAPI automatically converts to JSON
        
    Example:
        curl -X POST http://127.0.0.1:8000/shorten \\
             -H "Content-Type: application/json" \\
             -d '{"original_url": "https://google.com"}'
        
        Returns: {"short_url": "http://127.0.0.1:8000/4c93", ...}
        
    OOP CONCEPTS:
        - DEPENDENCY INJECTION: Service is injected, not created
        - SEPARATION OF CONCERNS: This function handles HTTP, service handles logic
        - SINGLE RESPONSIBILITY: Only responsible for HTTP request/response
    """
    
    # STEP 1: Call the service to create a short code
    # service.create_short_code() handles all the business logic:
    # - Saves URL to database
    # - Generates unique ID
    # - Encodes ID to Base62
    # - Updates database with short code
    # - Returns the short code
    #
    # str(request.original_url): Convert HttpUrl object to string
    # request.original_url is an HttpUrl object (Pydantic type)
    # The service expects a plain string, so we convert it
    short_hash = service.create_short_code(str(request.original_url))
    
    # STEP 2: Log the operation
    # logger.info() writes an informational message to the log
    # %s placeholders are filled with the values (short_hash, request.original_url)
    # This helps with debugging and monitoring in production
    # Example log: "INFO: Created short URL 4c93 for https://google.com"
    logger.info("Created short URL %s for %s", short_hash, request.original_url)
    
    # STEP 3: Build and return the response
    # URLCreateResponse is a Pydantic model (from schemas.py)
    # We create an instance with the short_url and original_url
    #
    # F-STRING: f"{BASE_URL}/{short_hash}"
    # Combines strings: "http://127.0.0.1:8000" + "/" + "4c93"
    # Result: "http://127.0.0.1:8000/4c93"
    #
    # FastAPI sees the return type is URLCreateResponse
    # It automatically:
    # - Validates the response matches the schema
    # - Converts the Pydantic object to JSON
    # - Sends it as the HTTP response body
    # - Sets Content-Type: application/json header
    return URLCreateResponse(
        short_url=f"{BASE_URL}/{short_hash}",
        original_url=str(request.original_url),
    )


# ============================================================================
# ROUTE: GET /{short_hash} - Redirect to original URL
# ============================================================================
# This endpoint receives a short code and redirects to the original URL.
#
# HTTP METHOD: GET
# - Used for retrieving resources
# - No request body (data is in the URL path)
# - Returns a redirect response (302 status code)
#
# PATH PARAMETER: {short_hash}
# - Curly braces {} indicate a variable part of the URL
# - Example: GET /abc123 → short_hash="abc123"
# - FastAPI extracts this and passes it to the function parameter
#
# DECORATORS EXPLAINED:
# @router.get("/{short_hash}") registers this as a GET endpoint
# - Matches any GET request to /ANYTHING (where ANYTHING is captured as short_hash)
# - Must be defined AFTER specific routes like /admin/database
#   (otherwise /admin/database would match {short_hash} and fail!)
# ============================================================================
@router.get("/{short_hash}")
async def redirect_to_original(
    short_hash: str,
    background_tasks: BackgroundTasks,
    service: UrlShortenerService = Depends(get_url_service),
):
    """
    Redirect from short URL to original URL.
    
    This endpoint is what makes the URL shortener useful!
    When someone visits a short URL, they're redirected to the original.
    
    HTTP Request:
        Method: GET
        Path: /{short_hash}
        Example: http://127.0.0.1:8000/abc123
        
    HTTP Response:
        Status: 302 Found (redirect)
        Headers: Location: https://www.example.com/original/path
        
    What happens:
        1. User clicks short URL (http://127.0.0.1:8000/abc123)
        2. Browser sends GET /abc123 to our API
        3. API looks up original URL in database
        4. API returns 302 redirect with Location header
        5. Browser automatically navigates to original URL
        6. Click is tracked in background (doesn't delay redirect)
    
    Args:
        short_hash: The short code from the URL path
                   FastAPI extracts this from the URL automatically
                   Example: GET /abc123 → short_hash="abc123"
                   
        background_tasks: FastAPI's background task manager
                         Allows running tasks AFTER the response is sent
                         Great for logging, analytics, cleanup, etc.
                         Doesn't delay the response to the user
                         
        service: The URL shortener service (DEPENDENCY INJECTION)
                Injected automatically by FastAPI via Depends()
        
    Returns:
        RedirectResponse: Special response that redirects the browser
                         Contains status_code=302 and Location header
        
    Raises:
        HTTPException: If short_hash is not found in database
                      Returns 404 Not Found to the user
        
    Example:
        # Create a short URL first
        curl -X POST http://127.0.0.1:8000/shorten \\
             -d '{"original_url": "https://google.com"}'
        # Returns: {"short_url": "http://127.0.0.1:8000/4c93"}
        
        # Visit the short URL (in browser or with curl)
        curl -L http://127.0.0.1:8000/4c93
        # Browser is redirected to https://google.com
        # Click count is incremented in background
        
    OOP CONCEPTS:
        - SEPARATION OF CONCERNS: HTTP handling vs business logic vs analytics
        - SINGLE RESPONSIBILITY: This function only handles HTTP redirect
        - DEPENDENCY INJECTION: Service is provided by FastAPI
    """
    
    # STEP 1: Look up the original URL
    # service.resolve_url() queries the database for this short_hash
    # Returns the original URL if found, None if not found
    original_url = service.resolve_url(short_hash)
    
    # STEP 2: Handle "not found" case
    # If original_url is None, the short_hash doesn't exist in the database
    # We raise an HTTPException to return a 404 error to the user
    #
    # HTTPException: Special FastAPI exception that becomes an HTTP response
    # - status_code=404: HTTP 404 Not Found
    # - detail: Error message sent to user (appears in response body)
    #
    # BOOLEAN CHECK: if not original_url:
    # - If original_url is None, this is True
    # - If original_url is a string (even empty), this is False
    # - This is "truthy/falsy" checking in Python
    if not original_url:
        # Log a warning (more serious than info, less than error)
        logger.warning("Short hash not found: %s", short_hash)
        
        # Raise an exception that FastAPI catches and converts to HTTP 404
        # When this is raised, the function stops executing
        # FastAPI returns: {"detail": "Short URL not found in database"}
        # with status code 404
        raise HTTPException(status_code=404, detail="Short URL not found in database")

    # STEP 3: Track the click in the background
    # BackgroundTasks allows us to run code AFTER the response is sent
    # This means the redirect happens immediately, tracking happens after
    # User doesn't wait for the database update - better user experience!
    #
    # background_tasks.add_task(function, *args, **kwargs)
    # - function: The function to call (service.track_click)
    # - *args: Arguments to pass (short_hash)
    #
    # EXECUTION ORDER:
    # 1. This line schedules the task (doesn't run it yet)
    # 2. Function continues to return the redirect
    # 3. FastAPI sends the redirect response to user
    # 4. AFTER response is sent, FastAPI runs service.track_click(short_hash)
    #
    # WHY IN BACKGROUND?
    # - PERFORMANCE: User gets redirected instantly (no wait for DB write)
    # - RELIABILITY: If tracking fails, redirect still works
    # - SEPARATION: Analytics don't block core functionality
    background_tasks.add_task(service.track_click, short_hash)
    
    # STEP 4: Log the redirect (for monitoring/debugging)
    logger.info("Redirecting %s to %s", short_hash, original_url)
    
    # STEP 5: Return the redirect response
    # RedirectResponse is a special FastAPI response class
    # - url=original_url: Where to redirect to
    # - status_code=302: HTTP 302 "Found" (temporary redirect)
    #
    # HTTP REDIRECT STATUS CODES:
    # - 301: Permanent redirect (browsers cache this)
    # - 302: Temporary redirect (used here - don't cache)
    # - 307: Temporary redirect (preserves HTTP method)
    #
    # When browser receives this response:
    # 1. Sees status code 302
    # 2. Reads Location header (set by RedirectResponse)
    # 3. Automatically makes a new request to that URL
    # 4. User ends up on the original URL
    return RedirectResponse(url=original_url, status_code=302)


# ============================================================================
# ROUTE: GET /admin/database - View all URLs (Admin endpoint)
# ============================================================================
# This endpoint returns all stored URLs with their statistics.
#
# HTTP METHOD: GET
# - Used for retrieving resources
# - No request body
# - Returns JSON with all URL data
#
# SECURITY WARNING:
# - This endpoint has NO AUTHENTICATION
# - Anyone can view all your URLs!
# - In production, add authentication (API keys, OAuth, etc.)
# - Or remove this endpoint entirely
#
# PATH ORDER:
# - This must be defined BEFORE @router.get("/{short_hash}")
# - Otherwise, "/admin/database" would match {short_hash} pattern
# - FastAPI matches routes in the order they're defined
# ============================================================================
@router.get("/admin/database")
async def view_database(db: UrlRepository = Depends(get_db)):
    """
    Admin endpoint: View all stored URLs and their statistics.
    
    This is a debugging/admin tool to see what's in the database.
    Useful for development, testing, and monitoring.
    
    HTTP Request:
        Method: GET
        Path: /admin/database
        No body required
        
    HTTP Response:
        Status: 200 OK
        Body: {
            "total_urls_stored": 5,
            "database_contents": {
                "abc123": {
                    "url_id": 1,
                    "original_url": "https://example.com/path1",
                    "click_count": 10
                },
                "def456": {
                    "url_id": 2,
                    "original_url": "https://example.com/path2",
                    "click_count": 5
                }
            }
        }
    
    Args:
        db: The database repository (DEPENDENCY INJECTION)
           FastAPI calls get_db() and injects the result
           This gives direct access to the database layer
           
           Note: We inject the repository, not the service
           Why? Because we just want to read all data,
           no business logic needed
    
    Returns:
        dict: Dictionary containing count and all URL records
             FastAPI automatically converts to JSON
        
    Example:
        curl http://127.0.0.1:8000/admin/database
        # Returns all URLs with their stats
        
    Security considerations:
        - NO AUTHENTICATION: Anyone can call this!
        - PRIVACY RISK: Exposes all URLs in your database
        - PERFORMANCE: Returns ALL records (could be slow for large databases)
        
    For production:
        - Add authentication (require API key or login)
        - Add authorization (only admins can access)
        - Add pagination (limit records returned)
        - Add filtering (search by date, URL, etc.)
        - Or completely remove this endpoint
        
    OOP CONCEPTS:
        - DEPENDENCY INJECTION: Repository is injected
        - SEPARATION OF CONCERNS: Direct data access for admin purposes
        - SINGLE RESPONSIBILITY: Only returns database contents
    """
    
    # STEP 1: Get all URL records from the database
    # db.get_all() returns a dictionary of all URLs
    # Format: {short_hash: {url_id, original_url, click_count}}
    #
    # This is a SNAPSHOT of the database at this moment
    # Other requests might be modifying the database concurrently
    # But this snapshot is consistent (thanks to database locks)
    snapshot = db.get_all()
    
    # STEP 2: Build and return the response
    # We wrap the data in a dictionary with two fields:
    # - total_urls_stored: Count of URLs (for convenience)
    # - database_contents: The actual URL data
    #
    # len(snapshot): Gets the number of items in the dictionary
    # This tells us how many URLs are stored
    #
    # FastAPI automatically:
    # - Converts this dict to JSON
    # - Sets Content-Type: application/json header
    # - Sends it as the response body
    #
    # RETURN TYPE:
    # - We don't specify a response_model decorator
    # - FastAPI infers the type from the return statement
    # - It sees a dict and converts it to JSON
    return {
        "total_urls_stored": len(snapshot),
        "database_contents": snapshot,
    }


# ============================================================================
# KEY OOP CONCEPTS DEMONSTRATED IN THIS FILE:
# ============================================================================
# 1. SEPARATION OF CONCERNS
#    - Routes: Handle HTTP (request parsing, response building)
#    - Service: Handle business logic (create short codes, resolve URLs)
#    - Repository: Handle data persistence (database operations)
#    - Each layer has a distinct responsibility
#
# 2. DEPENDENCY INJECTION
#    - Services and repositories are injected via Depends()
#    - Routes don't create these objects
#    - Easy to swap implementations (mock for testing)
#    - FastAPI handles the injection automatically
#
# 3. SINGLE RESPONSIBILITY PRINCIPLE
#    - create_short_url: Only handles POST /shorten endpoint
#    - redirect_to_original: Only handles GET /{short_hash} endpoint
#    - view_database: Only handles GET /admin/database endpoint
#    - Each function does ONE thing
#
# 4. ENCAPSULATION
#    - Routes don't know about SQL, Base62 encoding, or database details
#    - They just call simple service methods
#    - Implementation details are hidden behind clean interfaces
#
# 5. INTERFACE SEGREGATION
#    - Routes depend on UrlShortenerService interface
#    - Don't care about the specific implementation
#    - Service could use SQLite, PostgreSQL, or even a remote API
#
# 6. ASYNC/AWAIT
#    - All route functions are marked 'async'
#    - Allows FastAPI to handle multiple requests concurrently
#    - While one request waits for database, others can execute
#    - Better performance for I/O-bound operations
#
# 7. DECORATOR PATTERN
#    - @router.post(), @router.get() are decorators
#    - They wrap the function with additional behavior
#    - They register the function as a route handler
#    - Clean syntax for route registration
#
# 8. TYPE HINTS
#    - All parameters and returns have type annotations
#    - Helps IDEs provide auto-completion
#    - FastAPI uses these for validation and documentation
#    - Catches errors at development time
#
# 9. BACKGROUND TASKS
#    - Click tracking doesn't block the redirect response
#    - Improves user experience (faster responses)
#    - Separates critical path from analytics
#    - Demonstrates async programming concepts
#
# 10. ERROR HANDLING
#    - HTTPException provides clean error responses
#    - FastAPI converts exceptions to proper HTTP responses
#    - Logging helps with debugging and monitoring
#    - Users get helpful error messages
# ============================================================================