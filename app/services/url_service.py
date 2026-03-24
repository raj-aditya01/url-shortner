# ============================================================================
# URL_SERVICE.PY - BUSINESS LOGIC LAYER (SERVICE LAYER)
# ============================================================================
# This file contains the BUSINESS LOGIC for URL shortening.
#
# WHAT IS A SERVICE LAYER?
# - Contains the core business rules and workflows
# - Sits between the API routes (presentation) and database (data)
# - Coordinates actions that might involve multiple steps
#
# WHY USE A SERVICE LAYER?
# - SEPARATION OF CONCERNS: HTTP stuff stays in routes, business logic here
# - REUSABILITY: Can be used by API, CLI, background jobs, etc.
# - TESTABILITY: Easy to test without involving HTTP or databases
# - MAINTAINABILITY: Business rules are in one place, not scattered
#
# ARCHITECTURE LAYERS:
# ┌──────────────────┐
# │  API Routes      │  ← Handles HTTP (requests/responses)
# └────────┬─────────┘
#          ↓
# ┌────────▼─────────┐
# │  Service Layer   │  ← Handles BUSINESS LOGIC (this file!)
# └────────┬─────────┘
#          ↓
# ┌────────▼─────────┐
# │  Repository      │  ← Handles DATABASE operations
# └──────────────────┘
# ============================================================================

# IMPORTS
# ----------------------------------------------------------------------------
# This import enables forward references in type hints
# Allows us to use class names before they're fully defined
from __future__ import annotations

# Import the repository interface and the encoder utility
from app.repositories.url_repository import UrlRepository
from app.services.base62_encoder import Base62Encoder


# ============================================================================
# CLASS: UrlShortenerService
# ============================================================================
# This is a SERVICE CLASS that implements the URL shortening business logic.
#
# OOP CONCEPT: COMPOSITION
# - This class contains a UrlRepository (has-a relationship)
# - Instead of inheriting from UrlRepository (is-a), it uses one
# - Composition is often better than inheritance: "has-a" vs "is-a"
#
# OOP CONCEPT: DEPENDENCY INJECTION
# - The repository is passed in via the constructor
# - The service doesn't create its own repository
# - This makes the service flexible and testable
#
# RESPONSIBILITIES:
# 1. Create short codes from URLs (orchestrates repository + encoder)
# 2. Resolve short codes back to original URLs
# 3. Track clicks/statistics
# ============================================================================
class UrlShortenerService:
    """
    Service that handles URL shortening business logic.
    
    This class orchestrates the URL shortening workflow:
    - Takes a long URL and creates a short code
    - Looks up original URLs from short codes
    - Tracks usage statistics
    
    It coordinates between the repository (database) and encoder (Base62).
    
    OOP PRINCIPLES APPLIED:
    - SINGLE RESPONSIBILITY: Only handles URL shortening logic
    - DEPENDENCY INVERSION: Depends on UrlRepository interface, not concrete class
    - COMPOSITION: Uses a repository, doesn't inherit from it
    """

    # ========================================================================
    # CONSTRUCTOR: __init__
    # ========================================================================
    # This is a special method called when creating a new instance.
    # Syntax: service = UrlShortenerService(repository)
    #
    # PARAMETERS:
    #   self: Reference to the instance being created (automatic)
    #   repository: The database repository to use (DEPENDENCY INJECTION)
    #
    # RETURN TYPE HINT: -> None
    #   __init__ doesn't return a value (Python automatically returns the instance)
    #
    # OOP CONCEPT: INITIALIZATION
    # - Sets up the initial state of the object
    # - Stores the repository for later use in methods
    # ========================================================================
    def __init__(self, repository: UrlRepository) -> None:
        """
        Initialize the URL shortener service.
        
        Args:
            repository: The database repository to use for storing/retrieving URLs
                       This is DEPENDENCY INJECTION - we receive it, don't create it
                       Type is UrlRepository (interface), not a specific implementation
                       Could be SQLiteUrlRepository, PostgresUrlRepository, MockUrlRepository, etc.
        
        Example:
            repo = SQLiteUrlRepository("path/to/db")
            service = UrlShortenerService(repo)  # Injecting the dependency
            
        Why accept UrlRepository instead of SQLiteUrlRepository?
        - FLEXIBILITY: Can swap database implementations without changing this code
        - TESTABILITY: Can pass in a mock repository for testing
        - LOOSE COUPLING: Service doesn't depend on specific database implementation
        """
        
        # Store the repository in an INSTANCE VARIABLE
        # self._repository means this variable belongs to this specific instance
        # The underscore _ prefix is a Python convention meaning "internal/private"
        # It suggests: "Don't access this directly from outside the class"
        #
        # WHY STORE IT?
        # - All methods in this class need access to the repository
        # - Storing it in self makes it available to all methods
        # - Each instance of UrlShortenerService can have its own repository
        self._repository = repository

    # ========================================================================
    # METHOD: create_short_code
    # ========================================================================
    # This method creates a short code for a given URL.
    # It's the MAIN WORKFLOW for URL shortening.
    #
    # PARAMETERS:
    #   self: Reference to the current instance (automatic)
    #   original_url: The full URL to shorten (e.g., "https://example.com/long/path")
    #
    # RETURNS:
    #   str: The generated short code (e.g., "abc123")
    #
    # WORKFLOW (3 steps):
    #   1. Save URL to database and get its ID
    #   2. Encode the ID to a short string
    #   3. Update the database with the short code
    # ========================================================================
    def create_short_code(self, original_url: str) -> str:
        """
        Create and save a new short code for a URL.
        
        This is the main business logic method for URL shortening.
        It orchestrates multiple steps to create a short URL.
        
        Args:
            original_url: The full URL to be shortened
                         Example: "https://www.example.com/very/long/path"
            
        Returns:
            str: The short code (hash) that maps to this URL
                 Example: "abc123"
                 
        Workflow:
            1. Save the URL to database → get back an ID (e.g., 1000001)
            2. Encode that ID to Base62 → get short string (e.g., "4c93")  
            3. Update the database record with the short code
            4. Return the short code
            
        Example:
            service = UrlShortenerService(repository)
            short_code = service.create_short_code("https://google.com")
            # Returns: "4c93"
            # Database now has: ID=1000001, URL="https://google.com", hash="4c93"
            
        Why this workflow?
        - ATOMIC ID GENERATION: Database gives us a guaranteed unique ID
        - DETERMINISTIC ENCODING: Same ID always produces same short code
        - CONSISTENCY: Database has both the ID and the short code
        """
        
        # STEP 1: Save URL to database and get the assigned ID
        # self._repository: Access the repository we stored in __init__
        # .save_and_get_id(): Call a method on the repository
        # The repository returns a unique integer ID (e.g., 1000001)
        #
        # WHY GET THE ID?
        # - We'll encode it into the short code
        # - IDs are auto-incrementing, so each URL gets a unique number
        # - This guarantees unique short codes
        url_id = self._repository.save_and_get_id(original_url)
        
        # STEP 2: Encode the ID to a Base62 short string
        # Base62Encoder.encode(): Static method call on the encoder class
        # Converts: 1000001 → "4c93" (or similar)
        #
        # WHY BASE62?
        # - Much shorter than the decimal ID
        # - URL-safe characters only
        # - Still unique (each ID maps to one code)
        short_hash = Base62Encoder.encode(url_id)
        
        # STEP 3: Update the database record with the short code
        # We need to save the short_hash back to the database so we can look it up later
        # The record now has: id=1000001, original_url="...", short_hash="4c93"
        #
        # WHY UPDATE?
        # - Initially we saved without the short_hash (we didn't have it yet)
        # - Now we have it, so we update the record
        # - Later we can look up original_url by short_hash
        self._repository.update_short_hash(url_id, short_hash, original_url)
        
        # STEP 4: Return the short code
        # The caller (usually an API route) will use this to build the short URL
        # Example: If short_hash is "4c93", the route builds "http://127.0.0.1:8000/4c93"
        return short_hash

    # ========================================================================
    # METHOD: resolve_url
    # ========================================================================
    # This method looks up the original URL for a given short code.
    # Used when someone visits the short URL.
    #
    # PARAMETERS:
    #   self: Reference to the current instance
    #   short_hash: The short code to look up (e.g., "abc123")
    #
    # RETURNS:
    #   str | None: The original URL if found, None if not found
    #   The | operator means "or" (Python 3.10+ syntax)
    # ========================================================================
    def resolve_url(self, short_hash: str) -> str | None:
        """
        Look up the original URL for a given short code.
        
        This is used when someone clicks/visits a short URL.
        The API needs to know where to redirect them.
        
        Args:
            short_hash: The short code from the URL
                       Example: "4c93" (from http://127.0.0.1:8000/4c93)
            
        Returns:
            str: The original full URL if the short code exists
            None: If the short code is not found in the database
            
        Example:
            original = service.resolve_url("4c93")
            # Returns: "https://www.google.com"
            # Or returns: None if "4c93" doesn't exist
            
        Why return None instead of raising an error?
        - FLEXIBILITY: Let the caller decide how to handle missing URLs
        - CLEAN CODE: None is a clear signal that nothing was found
        - HTTP SEMANTICS: Caller can return 404 Not Found
        """
        
        # Delegate to the repository's get_original_url method
        # This is DELEGATION: passing work to another object
        # The service doesn't know HOW the repository finds the URL
        # It just knows it CAN find it
        #
        # This is the INTERFACE SEGREGATION principle:
        # - Service depends on what the repository CAN DO (interface)
        # - Not on HOW it does it (implementation)
        return self._repository.get_original_url(short_hash)

    # ========================================================================
    # METHOD: track_click
    # ========================================================================
    # This method increments the click counter for a short code.
    # Used for analytics/statistics.
    #
    # PARAMETERS:
    #   self: Reference to the current instance
    #   short_hash: The short code that was clicked
    #
    # RETURNS:
    #   None: This method doesn't return anything (void method)
    # ========================================================================
    def track_click(self, short_hash: str) -> None:
        """
        Increase the click count for a short code.
        
        This tracks how many times a short URL has been visited.
        Useful for analytics and statistics.
        
        Args:
            short_hash: The short code being clicked/visited
                       Example: "4c93"
            
        Returns:
            None (this method performs an action but doesn't return a value)
            
        Example:
            service.track_click("4c93")
            # Database click_count for "4c93" goes from 5 to 6
            
        Why a separate method instead of doing this in resolve_url?
        - SEPARATION OF CONCERNS: Resolving and tracking are different actions
        - FLEXIBILITY: Can track clicks in background (doesn't delay the redirect)
        - TESTABILITY: Can test resolve and tracking independently
        
        Note: In url_routes.py, this is called as a background task
              so it doesn't slow down the redirect response
        """
        
        # Again, DELEGATION to the repository
        # The service doesn't know HOW clicks are tracked
        # It just knows the repository CAN track them
        #
        # The repository handles the SQL: UPDATE url_mappings SET click_count = click_count + 1 ...
        self._repository.increment_click_count(short_hash)


# ============================================================================
# KEY OOP CONCEPTS DEMONSTRATED HERE:
# ============================================================================
# 1. SINGLE RESPONSIBILITY PRINCIPLE (SRP)
#    - This class has ONE job: coordinate URL shortening logic
#    - It doesn't handle HTTP (that's the routes layer)
#    - It doesn't handle SQL (that's the repository layer)
#    - It doesn't handle encoding (that's Base62Encoder)
#    - It ORCHESTRATES these pieces to implement the business workflow
#
# 2. DEPENDENCY INJECTION & INVERSION
#    - Receives repository via constructor (injection)
#    - Depends on UrlRepository interface, not concrete implementation
#    - This is the "D" in SOLID: Depend on abstractions, not concretions
#
# 3. COMPOSITION OVER INHERITANCE
#    - Uses a repository (has-a relationship)
#    - Doesn't inherit from it (is-a relationship)
#    - More flexible: can easily swap or mock the repository
#
# 4. ENCAPSULATION
#    - Implementation details are hidden
#    - Users call simple methods like create_short_code()
#    - They don't need to know about database IDs, Base62, etc.
#    - Internal details (like _repository) are marked private with _
#
# 5. DELEGATION
#    - Service delegates data operations to repository
#    - Service delegates encoding to Base62Encoder
#    - Each component does what it's best at
#
# 6. INTERFACE SEGREGATION
#    - Service uses UrlRepository interface
#    - Doesn't care if it's SQLite, PostgreSQL, or in-memory
#    - Easy to swap implementations
#
# 7. METHOD DESIGN
#    - Each method has a clear purpose and name
#    - Parameters and return types are clearly documented
#    - Methods are small and focused
# ============================================================================
