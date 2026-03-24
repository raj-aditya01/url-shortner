# ============================================================================
# DEPENDENCIES.PY - DEPENDENCY INJECTION CONTAINER
# ============================================================================
# This file creates SINGLETON instances of our service and repository.
#
# WHAT IS DEPENDENCY INJECTION?
# - Instead of creating objects inside a function, we "inject" (pass in) them
# - Example WITHOUT DI:  def my_function(): db = Database()  # Creates here
# - Example WITH DI:     def my_function(db: Database):      # Receives here
#
# WHY USE DEPENDENCY INJECTION?
# - TESTABILITY: Easy to pass in mock/fake objects for testing
# - FLEXIBILITY: Easy to swap implementations (SQLite -> PostgreSQL)
# - REUSABILITY: Same instance can be shared across multiple requests
# - SINGLE RESPONSIBILITY: Functions focus on their logic, not object creation
#
# WHAT IS A SINGLETON?
# - A SINGLETON is an object that's created only ONCE and reused everywhere
# - Instead of creating a new database connection for every request,
#   we create ONE connection and share it across all requests
# - This saves memory and improves performance
# ============================================================================

# IMPORTS
# ----------------------------------------------------------------------------
# This import allows us to use type hints that reference classes not yet defined
from __future__ import annotations

# os: Access environment variables like SQLITE_DB_PATH
import os

# Path: Modern way to work with file paths (instead of string manipulation)
from pathlib import Path

# Our custom classes for database and business logic
from app.repositories.url_repository import SQLiteUrlRepository, UrlRepository
from app.services.url_service import UrlShortenerService


# ============================================================================
# SECTION 1: CREATE THE SINGLETON INSTANCES
# ============================================================================
# These lines run ONCE when the module is first imported
# The objects are stored in MODULE-LEVEL variables (starting with _)
# The underscore _ prefix is a Python convention meaning "private/internal"
# ============================================================================

# STEP 1: Find the project root directory
# __file__ is the current file path: C:\Users\USER\training\1603\app\dependencies.py
# .parent gives us: C:\Users\USER\training\1603\app
# .parent.parent gives us: C:\Users\USER\training\1603
_project_root = Path(__file__).parent.parent

# STEP 2: Determine database file path
# os.getenv() tries to read an environment variable called "SQLITE_DB_PATH"
# If not set, it uses the default: project_root/data/url_shortener.db
# .resolve() converts it to an absolute path (full path from C:\)
#
# Example: If SQLITE_DB_PATH is not set:
# Result: C:\Users\USER\training\1603\data\url_shortener.db
_db_path = Path(os.getenv("SQLITE_DB_PATH", str(_project_root / "data" / "url_shortener.db"))).resolve()

# STEP 3: Create the data directory if it doesn't exist
# .parent gives us the directory containing the file (data/)
# mkdir() creates the directory
# parents=True: Also create parent directories if needed
# exist_ok=True: Don't error if directory already exists
_db_path.parent.mkdir(parents=True, exist_ok=True)

# STEP 4: Create the SINGLETON repository instance
# This creates ONE database connection that will be reused
# str(_db_path) converts the Path object to a string for SQLite
# This is DEPENDENCY INJECTION: we pass the db_path to SQLiteUrlRepository
_repository = SQLiteUrlRepository(str(_db_path))

# STEP 5: Create the SINGLETON service instance
# This creates ONE service that will be reused
# We pass _repository to the service (DEPENDENCY INJECTION again!)
# The service doesn't create its own repository - it receives one
_service = UrlShortenerService(_repository)


# ============================================================================
# SECTION 2: DEPENDENCY PROVIDER FUNCTIONS
# ============================================================================
# These functions are used by FastAPI's Depends() system
# When a route needs a service or repository, FastAPI calls these functions
#
# Example in url_routes.py:
#   def create_short_url(service: UrlShortenerService = Depends(get_url_service)):
#       # FastAPI automatically calls get_url_service() and passes result here
#
# This pattern is called DEPENDENCY INJECTION via FUNCTION DEPENDENCIES
# ============================================================================

def get_db() -> UrlRepository:
    """
    Provide the database repository instance to any route that needs it.
    
    This function is used with FastAPI's Depends() mechanism:
        @app.get("/example")
        def example(db: UrlRepository = Depends(get_db)):
            # 'db' will be the _repository singleton instance
    
    Returns:
        UrlRepository: The singleton database repository instance
        
    Why return UrlRepository type instead of SQLiteUrlRepository?
    - ABSTRACTION: The caller doesn't need to know if it's SQLite, PostgreSQL, etc.
    - FLEXIBILITY: We can swap SQLite for another database without changing routes
    - This is the INTERFACE SEGREGATION principle from SOLID (OOP principles)
    """
    return _repository


def get_url_service() -> UrlShortenerService:
    """
    Provide the URL shortener service instance to any route that needs it.
    
    This function is used with FastAPI's Depends() mechanism:
        @app.post("/shorten")
        def shorten(service: UrlShortenerService = Depends(get_url_service)):
            # 'service' will be the _service singleton instance
    
    Returns:
        UrlShortenerService: The singleton URL shortener service instance
        
    Why use a function instead of directly accessing _service?
    - FLEXIBILITY: We could add logic like logging, authentication checks, etc.
    - TESTABILITY: Tests can override this function to return mock services
    - CONSISTENCY: Follows FastAPI's dependency injection pattern
    """
    return _service


# ============================================================================
# KEY OOP CONCEPTS DEMONSTRATED HERE:
# ============================================================================
# 1. SINGLETON PATTERN: Creating one instance and reusing it (_repository, _service)
# 
# 2. DEPENDENCY INJECTION: Passing dependencies instead of creating them
#    - UrlShortenerService receives a repository (doesn't create one)
#    - Routes receive a service (don't create one)
#
# 3. ENCAPSULATION: Implementation details are hidden
#    - Routes don't know if database is SQLite, PostgreSQL, etc.
#    - They just know it follows the UrlRepository interface
#
# 4. INTERFACE SEGREGATION: Using abstract types (UrlRepository)
#    - get_db() returns UrlRepository, not SQLiteUrlRepository
#    - This allows swapping implementations without changing code
#
# 5. SINGLE RESPONSIBILITY: Each piece has one job
#    - This file: Create and provide dependencies
#    - Repository: Handle database operations  
#    - Service: Handle business logic
#    - Routes: Handle HTTP requests
# ============================================================================
