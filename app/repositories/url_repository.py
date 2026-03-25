# ============================================================================
# URL_REPOSITORY.PY - DATA ACCESS LAYER (REPOSITORY PATTERN)
# ============================================================================
# This file handles ALL database operations for URLs.
#
# WHAT IS THE REPOSITORY PATTERN?
# - A design pattern that separates data access logic from business logic
# - Acts as a "middleman" between your application and the database
# - Provides a simple interface for data operations (save, get, update, delete)
#
# WHY USE THE REPOSITORY PATTERN?
# - ABSTRACTION: Hide database details from the rest of the app
# - FLEXIBILITY: Easy to swap databases (SQLite → PostgreSQL → MongoDB)
# - TESTABILITY: Easy to create mock/fake repositories for testing
# - MAINTAINABILITY: All data logic in one place
# - SINGLE RESPONSIBILITY: Only responsible for data access
#
# ARCHITECTURE:
# ┌──────────────────────────────────────────────────────────┐
# │  Service Layer (UrlShortenerService)                     │
# │  "I need to save a URL"                                  │
# └────────────────────────┬─────────────────────────────────┘
#                          ↓
# ┌────────────────────────▼─────────────────────────────────┐
# │  UrlRepository Interface (Protocol)                      │
# │  "Any repository must have these methods"                │
# └────────────────────────┬─────────────────────────────────┘
#                          ↓
#          ┌───────────────┴───────────────┐
#          ↓                               ↓
# ┌────────▼──────────┐        ┌──────────▼─────────┐
# │ MockUrlRepository │        │ SQLiteUrlRepository│
# │ (in-memory dict)  │        │ (real database)    │
# └───────────────────┘        └────────────────────┘
# ============================================================================

# IMPORTS
# ----------------------------------------------------------------------------
# Allows forward references in type hints
from __future__ import annotations

# sqlite3: Python's built-in SQLite database library
import sqlite3

# Lock: Ensures thread-safe access to shared resources (prevents race conditions)
from threading import Lock

# Type hints for better code documentation and IDE support
# Dict: Dictionary type hint (Dict[str, dict] means keys are strings, values are dicts)
# Optional: Indicates a value can be of a type OR None (Optional[str] = str | None)
# Protocol: Defines an interface (like an abstract class but more flexible)
from typing import Dict, Optional, Protocol


# ============================================================================
# CLASS: UrlRepository (Protocol)
# ============================================================================
# This is a PROTOCOL (also called an INTERFACE in other languages).
# It defines a CONTRACT: "Any repository must have these methods."
#
# OOP CONCEPT: INTERFACE / PROTOCOL
# - Defines WHAT methods must exist, not HOW they work
# - Like a promise: "I guarantee these methods will be available"
# - Multiple classes can implement the same protocol differently
#
# WHY USE A PROTOCOL?
# - POLYMORPHISM: Different implementations, same interface
# - FLEXIBILITY: Swap implementations without changing other code
# - TESTING: Easy to create mock implementations
# - DOCUMENTATION: Clear contract of what a repository must do
#
# REAL-WORLD ANALOGY:
# - Think of a "Vehicle" protocol with methods: start(), stop(), drive()
# - Car, Motorcycle, Truck all implement these methods differently
# - But any code that needs a Vehicle can use any of them
# ============================================================================
class UrlRepository(Protocol):
    """
    Interface (Protocol) that defines all database operations for URLs.
    
    This is a CONTRACT that any URL repository must follow.
    Any class implementing these methods can be used as the storage layer.
    
    OOP PRINCIPLE: DEPENDENCY INVERSION
    - High-level code (Service) depends on this interface
    - Not on concrete implementations (SQLiteUrlRepository, MockUrlRepository)
    - This is the "D" in SOLID principles
    
    PROTOCOL vs ABSTRACT BASE CLASS:
    - Protocol: Duck typing ("if it walks like a duck...")
    - ABC: Explicit inheritance required
    - Protocol is more flexible and Pythonic
    
    Example usage:
        # Any class with these methods can be a UrlRepository
        def my_function(repo: UrlRepository):
            # Can pass SQLiteUrlRepository, MockUrlRepository, etc.
            url_id = repo.save_and_get_id("https://example.com")
    """

    # ========================================================================
    # INTERFACE METHOD: save_and_get_id
    # ========================================================================
    # The ... (Ellipsis) means "implementation not provided"
    # Classes implementing this protocol MUST provide this method
    # ========================================================================
    def save_and_get_id(self, original_url: str) -> int:
        """
        Save a URL and return its auto-generated ID.
        
        Args:
            original_url: The full URL to save
            
        Returns:
            int: The unique ID assigned to this URL
            
        Contract:
            - Must save the URL to storage
            - Must return a unique integer ID
            - ID should be auto-incrementing or otherwise guaranteed unique
        """
        ...  # Ellipsis indicates "must be implemented by concrete classes"

    # ========================================================================
    # INTERFACE METHOD: update_short_hash
    # ========================================================================
    def update_short_hash(self, url_id: int, short_hash: str, original_url: str) -> None:
        """
        Update a URL record with its generated short code.
        
        Args:
            url_id: The unique ID of the URL record
            short_hash: The Base62 encoded short code (e.g., "abc123")
            original_url: The original URL (for consistency)
            
        Returns:
            None
            
        Contract:
            - Must update the record identified by url_id
            - Must store the short_hash for later lookup
            - Should be idempotent (calling twice with same values is safe)
        """
        ...

    # ========================================================================
    # INTERFACE METHOD: get_original_url
    # ========================================================================
    def get_original_url(self, short_hash: str) -> Optional[str]:
        """
        Retrieve the original URL for a given short code.
        
        Args:
            short_hash: The short code to look up (e.g., "abc123")
            
        Returns:
            str: The original URL if found
            None: If the short code doesn't exist
            
        Contract:
            - Must return the exact URL that was stored
            - Must return None (not raise an error) if not found
            - Should be fast (used on every redirect)
        """
        ...

    # ========================================================================
    # INTERFACE METHOD: increment_click_count
    # ========================================================================
    def increment_click_count(self, short_hash: str) -> None:
        """
        Increment the click counter for a short code.
        
        Args:
            short_hash: The short code being accessed
            
        Returns:
            None
            
        Contract:
            - Must increase the click count by 1
            - Should be thread-safe (multiple clicks at once)
            - Should not fail if short_hash doesn't exist (silent ignore is OK)
        """
        ...

    # ========================================================================
    # INTERFACE METHOD: get_all
    # ========================================================================
    def get_all(self) -> Dict[str, dict]:
        """
        Retrieve all stored URL mappings.
        
        Returns:
            Dict[str, dict]: Dictionary mapping short codes to URL records
                            Format: {
                                "abc123": {
                                    "url_id": 1000001,
                                    "original_url": "https://example.com",
                                    "click_count": 5
                                }
                            }
            
        Contract:
            - Must return all URLs that have short codes
            - Must include url_id, original_url, and click_count for each
            - Used for admin/debugging, doesn't need to be super fast
        """
        ...


# ============================================================================
# CLASS: MockUrlRepository
# ============================================================================
# This is a CONCRETE IMPLEMENTATION of the UrlRepository protocol.
# It stores data in memory (Python dictionary) instead of a database.
#
# OOP CONCEPT: POLYMORPHISM
# - Implements the same interface as SQLiteUrlRepository
# - Can be used anywhere UrlRepository is expected
# - Different implementation, same contract
#
# WHY CREATE A MOCK REPOSITORY?
# - TESTING: Tests run faster without real database I/O
# - ISOLATION: Tests don't interfere with each other (fresh data each time)
# - SIMPLICITY: No need to set up/tear down database for tests
# - DEVELOPMENT: Can develop features before database is ready
#
# OOP CONCEPT: COMPOSITION
# - Uses a dictionary (self.db) to store data
# - Uses a Lock (self._lock) for thread safety
# - Composes simple objects to create more complex behavior
# ============================================================================
class MockUrlRepository:
    """
    In-memory storage implementation for testing and development.
    
    Stores URLs in a Python dictionary instead of a real database.
    Implements the UrlRepository protocol/interface.
    
    This is useful for:
    - Unit tests (fast, isolated)
    - Development (no database setup needed)
    - Demos (no persistent storage required)
    
    OOP PRINCIPLES:
    - SINGLE RESPONSIBILITY: Only handles in-memory storage
    - INTERFACE SEGREGATION: Implements UrlRepository protocol
    - THREAD SAFETY: Uses locks to prevent race conditions
    
    Data structure:
        self.db = {
            "abc123": {
                "url_id": 1000001,
                "original_url": "https://example.com",
                "click_count": 5
            },
            "def456": {...}
        }
    """

    # ========================================================================
    # CONSTRUCTOR: __init__
    # ========================================================================
    # Initializes the mock repository with empty storage.
    # ========================================================================
    def __init__(self) -> None:
        """
        Initialize the mock repository.
        
        Sets up:
        - Empty dictionary for storing URLs
        - Auto-increment counter starting at 1,000,000
        - Lock for thread-safe operations
        
        Why start at 1,000,000?
        - Makes IDs easily distinguishable from regular small numbers
        - Convention in many systems to start with a large number
        - Base62 encoding of 1000000+ looks good: "4c92" not "1" or "a"
        """
        
        # INSTANCE VARIABLE: Dictionary to store all URL mappings
        # Key: short_hash (str), Value: dict with url_id, original_url, click_count
        # Example: {"abc123": {"url_id": 1000001, "original_url": "...", "click_count": 0}}
        #
        # TYPE HINT: Dict[str, dict] means:
        # - Keys are strings (short hashes)
        # - Values are dictionaries (URL records)
        self.db: Dict[str, dict] = {}
        
        # INSTANCE VARIABLE: Counter for generating unique IDs
        # Starts at 1,000,000 and increments with each new URL
        # The underscore _ prefix indicates this is for internal use only
        # Python allows underscores in numbers for readability: 1_000_000 = 1000000
        self._auto_increment_id = 1_000_000
        
        # INSTANCE VARIABLE: Threading lock for concurrent access safety
        # WHY USE A LOCK?
        # - Web servers handle multiple requests simultaneously (multi-threaded)
        # - Two requests might try to save URLs at the same time
        # - Without a lock, they might get the same ID (race condition!)
        # - Lock ensures only one thread accesses critical sections at a time
        #
        # THREADING CONCEPT: RACE CONDITION
        # Without lock:
        #   Thread 1: read ID (1000001) → interrupted
        #   Thread 2: read ID (1000001) → increment → save (1000002)
        #   Thread 1: resume → increment → save (1000002) ← DUPLICATE!
        #
        # With lock:
        #   Thread 1: acquire lock → read → increment → save → release lock
        #   Thread 2: wait for lock → acquire → read → increment → save → release
        self._lock = Lock()

    # ========================================================================
    # METHOD: save_and_get_id
    # ========================================================================
    # Implements the UrlRepository protocol method.
    # Generates a new ID and "saves" the URL (stores in dictionary).
    # ========================================================================
    def save_and_get_id(self, original_url: str) -> int:
        """
        Save URL to memory and return its auto-generated ID.
        
        Args:
            original_url: The full URL to save
            
        Returns:
            int: The unique ID assigned (auto-incremented)
            
        Thread Safety:
            Uses self._lock to ensure atomic ID generation.
            Multiple threads calling this simultaneously will get unique IDs.
            
        Example:
            repo = MockUrlRepository()
            id1 = repo.save_and_get_id("https://google.com")  # Returns 1000001
            id2 = repo.save_and_get_id("https://github.com")  # Returns 1000002
        """
        
        # CONTEXT MANAGER: with self._lock:
        # This acquires the lock, executes the code block, then releases the lock
        # Even if an exception occurs, the lock is released (like try/finally)
        #
        # CRITICAL SECTION: Code inside the 'with' block
        # Only one thread can execute this at a time
        # Other threads wait until the lock is released
        with self._lock:
            # Increment the ID counter
            # This is the critical operation that needs protection
            # Without a lock, two threads might get the same ID
            self._auto_increment_id += 1
            
            # Return the new ID
            # Note: We don't actually store anything yet!
            # That happens in update_short_hash()
            # This mimics how SQLite works (INSERT returns ID, then UPDATE adds short_hash)
            return self._auto_increment_id

    # ========================================================================
    # METHOD: update_short_hash
    # ========================================================================
    # Stores the complete URL record in the dictionary.
    # ========================================================================
    def update_short_hash(self, url_id: int, short_hash: str, original_url: str) -> None:
        """
        Store the complete URL record with its short code.
        
        Args:
            url_id: The unique ID generated in save_and_get_id
            short_hash: The Base62 encoded short code (e.g., "abc123")
            original_url: The original URL
            
        Returns:
            None
            
        Thread Safety:
            Uses lock to ensure atomic updates to the dictionary.
            
        Example:
            repo.update_short_hash(1000001, "abc123", "https://google.com")
            # Now: repo.db["abc123"] = {"url_id": 1000001, "original_url": "...", "click_count": 0}
        """
        
        # CRITICAL SECTION: Updating shared dictionary
        with self._lock:
            # Store the URL record in the dictionary
            # KEY: short_hash (so we can look it up quickly)
            # VALUE: dictionary with all the URL details
            #
            # DICTIONARY LITERAL: {...} creates a new dict
            self.db[short_hash] = {
                "url_id": url_id,              # The database ID
                "original_url": original_url,  # The full URL
                "click_count": 0,              # Initialize click counter to 0
            }

    # ========================================================================
    # METHOD: get_original_url
    # ========================================================================
    # Looks up and returns the original URL for a short code.
    # ========================================================================
    def get_original_url(self, short_hash: str) -> Optional[str]:
        """
        Retrieve the original URL for a short code.
        
        Args:
            short_hash: The short code to look up (e.g., "abc123")
            
        Returns:
            str: The original URL if found
            None: If the short code doesn't exist
            
        No lock needed:
            Reading from dictionary is thread-safe in Python (GIL protection).
            Only writes need explicit locking.
            
        Example:
            url = repo.get_original_url("abc123")
            # Returns: "https://google.com" or None if not found
        """
        
        # DICTIONARY METHOD: .get(key, default=None)
        # Returns the value for key if it exists, otherwise returns None
        # Safer than db[key] which raises KeyError if key doesn't exist
        record = self.db.get(short_hash)
        
        # TERNARY EXPRESSION: value_if_true if condition else value_if_false
        # If record exists, return its original_url field
        # If record is None, return None
        #
        # This is equivalent to:
        #   if record:
        #       return record["original_url"]
        #   else:
        #       return None
        return record["original_url"] if record else None

    # ========================================================================
    # METHOD: increment_click_count
    # ========================================================================
    # Increases the click counter for a short code.
    # ========================================================================
    def increment_click_count(self, short_hash: str) -> None:
        """
        Increase the click counter for a short code by 1.
        
        Args:
            short_hash: The short code being accessed
            
        Returns:
            None
            
        Thread Safety:
            Uses lock because incrementing is a read-modify-write operation.
            Without lock: Thread1 reads 5, Thread2 reads 5, both write 6 (lost update!)
            With lock: Thread1 reads 5 writes 6, Thread2 reads 6 writes 7 (correct!)
            
        Example:
            repo.increment_click_count("abc123")
            # click_count goes from 5 to 6
        """
        
        # CRITICAL SECTION: Read-modify-write operation
        with self._lock:
            # Check if the short_hash exists in our database
            # The 'in' operator checks if a key exists in the dictionary
            if short_hash in self.db:
                # INCREMENT OPERATION: Read current value, add 1, write back
                # This is why we need a lock - this is not atomic without it
                # 
                # Breakdown:
                # 1. self.db[short_hash] - Get the record dictionary
                # 2. ["click_count"] - Access the click_count field
                # 3. += 1 - Add 1 to the current value
                self.db[short_hash]["click_count"] += 1
                # Note: If short_hash doesn't exist, we silently ignore it
                # This matches the protocol contract (don't fail on missing keys)

    # ========================================================================
    # METHOD: get_all
    # ========================================================================
    # Returns all stored URL mappings (for admin/debug purposes).
    # ========================================================================
    def get_all(self) -> Dict[str, dict]:
        """
        Return all stored URL mappings.
        
        Returns:
            Dict[str, dict]: The entire database dictionary
                            Format: {short_hash: {url_id, original_url, click_count}}
            
        Used for:
            - Admin interface to view all URLs
            - Debugging and testing
            - Analytics and reports
            
        Example:
            all_urls = repo.get_all()
            # Returns: {"abc123": {...}, "def456": {...}}
        """
        
        # Simply return the entire dictionary
        # In a real system, you might want to:
        # - Return a copy to prevent external modifications
        # - Add pagination for large datasets
        # - Add filtering/sorting options
        return self.db


# ============================================================================
# CLASS: SQLiteUrlRepository
# ============================================================================
# This is another CONCRETE IMPLEMENTATION of the UrlRepository protocol.
# It stores data in a SQLite database file (persistent storage).
#
# OOP CONCEPT: POLYMORPHISM (again!)
# - Implements the same interface as MockUrlRepository
# - Can be used interchangeably (same methods, different implementation)
# - Service layer doesn't know or care which one it's using
#
# WHY SQLITE?
# - ZERO CONFIGURATION: No server to install or configure
# - SERVERLESS: Database is just a file (easy backup, deploy)
# - RELIABLE: Battle-tested, used in millions of applications
# - PORTABLE: Works on Windows, Mac, Linux
# - FAST ENOUGH: Great for small to medium applications
#
# OOP CONCEPT: ENCAPSULATION
# - Hides all SQL complexity behind simple methods
# - Service layer never sees SQL - just calls methods
# - Could swap SQLite for PostgreSQL without changing service code
# ============================================================================
class SQLiteUrlRepository:
    """
    Persistent storage implementation using SQLite database.
    
    All data is saved to a SQLite database file on disk.
    Data persists across application restarts.
    Implements the UrlRepository protocol/interface.
    
    OOP PRINCIPLES:
    - SINGLE RESPONSIBILITY: Only handles SQLite database operations
    - INTERFACE SEGREGATION: Implements UrlRepository protocol
    - ENCAPSULATION: Hides SQL details from rest of application
    - THREAD SAFETY: Uses locks for concurrent access
    
    Database Schema:
        CREATE TABLE url_mappings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique ID for each URL
            original_url TEXT NOT NULL,            -- The full URL
            short_hash TEXT UNIQUE,                -- The short code (e.g., "abc123")
            click_count INTEGER NOT NULL DEFAULT 0 -- Number of times accessed
        )
    """

    # ========================================================================
    # CONSTRUCTOR: __init__
    # ========================================================================
    # Initializes the SQLite repository: connects to DB and creates table.
    # ========================================================================
    def __init__(self, db_path: str) -> None:
        """
        Initialize the SQLite repository.
        
        Args:
            db_path: Path to the SQLite database file
                    Example: "C:/Users/USER/training/1603/data/url_shortener.db"
                    If file doesn't exist, SQLite creates it automatically
        
        What happens during initialization:
            1. Create a lock for thread safety
            2. Connect to the SQLite database
            3. Configure the connection
            4. Create the url_mappings table if it doesn't exist
            
        Example:
            repo = SQLiteUrlRepository("data/urls.db")
            # Now ready to save/retrieve URLs
        """
        
        # INSTANCE VARIABLE: Lock for thread-safe database access
        # Same concept as MockUrlRepository - prevents race conditions
        # SQLite has its own internal locking, but we add extra safety
        self._lock = Lock()
        
        # INSTANCE VARIABLE: Database connection object
        # sqlite3.connect() opens or creates the database file
        #
        # PARAMETER: check_same_thread=False
        # By default, SQLite connections can only be used by the thread that created them
        # Setting this to False allows multiple threads to use the same connection
        # IMPORTANT: This is why we need self._lock - to prevent concurrent access
        #
        # sqlite3.connect() is like opening a file - it establishes communication with the DB
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        
        # CONFIGURE CONNECTION: Set row factory
        # By default, SQLite returns tuples: (1, "https://example.com", "abc123", 5)
        # With Row factory, we get dict-like objects: {"id": 1, "original_url": "...", ...}
        # This makes code more readable: row["original_url"] instead of row[1]
        #
        # sqlite3.Row is a special class that acts like both a tuple and a dict
        self._conn.row_factory = sqlite3.Row
        
        # Create the database table if it doesn't exist
        # This is a helper method defined below
        self._initialize_schema()

    # ========================================================================
    # METHOD: _initialize_schema (PRIVATE HELPER METHOD)
    # ========================================================================
    # Creates the database table structure.
    # The underscore _ prefix indicates this is a private method (internal use only).
    # ========================================================================
    def _initialize_schema(self) -> None:
        """
        Create the url_mappings table if it doesn't exist.
        
        This is called during __init__ to ensure the table exists.
        Uses CREATE TABLE IF NOT EXISTS so it's safe to call multiple times.
        
        Schema explanation:
            - id: Auto-incrementing integer (primary key)
            - original_url: The full URL (TEXT type, cannot be NULL)
            - short_hash: The short code (TEXT type, must be UNIQUE or NULL)
            - click_count: Number of clicks (INTEGER, defaults to 0)
            
        Why short_hash can be NULL:
            - We insert the URL first without a short_hash
            - Then we update it with the short_hash after encoding the ID
            - This is the two-step process: INSERT → get ID → encode → UPDATE
        """
        
        # CONTEXT MANAGER: with self._conn:
        # This starts a database TRANSACTION
        # If an error occurs, changes are rolled back automatically
        # If successful, changes are committed automatically
        #
        # TRANSACTION: A group of database operations that succeed or fail together
        # - ATOMICITY: All operations complete, or none do
        # - CONSISTENCY: Database is never left in a half-finished state
        # - ISOLATION: Other connections don't see partial changes
        # - DURABILITY: Committed changes are saved permanently
        # These are the ACID properties of databases
        with self._conn:
            # Execute the CREATE TABLE SQL statement
            # self._conn.execute() sends SQL to the database
            #
            # SQL BREAKDOWN:
            # - CREATE TABLE IF NOT EXISTS: Create only if table doesn't exist (safe to repeat)
            # - url_mappings: Table name
            # - id INTEGER PRIMARY KEY AUTOINCREMENT: Unique ID, auto-generates next value
            # - original_url TEXT NOT NULL: Text field, cannot be empty
            # - short_hash TEXT UNIQUE: Text field, must be unique across all rows (or NULL)
            # - click_count INTEGER NOT NULL DEFAULT 0: Integer field, defaults to 0 if not specified
            #
            # TRIPLE-QUOTED STRING: """ ... """
            # Allows multi-line strings without escape characters
            # Makes SQL more readable
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS url_mappings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_url TEXT NOT NULL,
                    short_hash TEXT UNIQUE,
                    click_count INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            
            # ================================================================
            # INITIALIZE AUTO-INCREMENT TO START AT 1,000,000
            # ================================================================
            # This ensures IDs start at 1,000,000 instead of 1
            # Why 1,000,000?
            # - Base62 encoding of small numbers (1-9) looks boring: "1", "2", "3"
            # - Base62 encoding of 1,000,000+ looks better: "4c92", "4c93", "4c94"
            # - Makes short URLs look more professional and random
            #
            # HOW IT WORKS:
            # SQLite's AUTOINCREMENT uses a special table called sqlite_sequence
            # We check if any URLs exist, and if not, we initialize the sequence
            # This only runs once when the table is first created
            #
            # Check if table is empty (no URLs inserted yet)
            cursor = self._conn.execute("SELECT COUNT(*) FROM url_mappings")
            count = cursor.fetchone()[0]
            
            # If table is empty, initialize the auto-increment sequence
            # This sets the next ID to be 1,000,000
            if count == 0:
                # Insert into sqlite_sequence to set the starting value
                # This table tracks the last ID used for AUTOINCREMENT columns
                # We set it to 999,999 so the next INSERT gets 1,000,000
                self._conn.execute(
                    """
                    INSERT OR REPLACE INTO sqlite_sequence (name, seq) 
                    VALUES ('url_mappings', 999999)
                    """
                )
                # Note: This only affects NEW databases
                # Existing databases keep their current sequence
                # To reset an existing database, delete data/url_shortener.db

    # ========================================================================
    # METHOD: save_and_get_id
    # ========================================================================
    # Inserts a new URL record and returns its auto-generated ID.
    # ========================================================================
    def save_and_get_id(self, original_url: str) -> int:
        """
        Save URL to database and return its auto-generated ID.
        
        Args:
            original_url: The full URL to save
            
        Returns:
            int: The unique ID assigned by SQLite (auto-increment)
            
        Thread Safety:
            Uses self._lock to ensure atomic INSERT + ID retrieval.
            
        SQL Operation:
            INSERT INTO url_mappings (original_url) VALUES ('https://example.com')
            
        Example:
            repo = SQLiteUrlRepository("data/urls.db")
            id1 = repo.save_and_get_id("https://google.com")  # Returns 1
            id2 = repo.save_and_get_id("https://github.com")  # Returns 2
        """
        
        # CRITICAL SECTION: INSERT and get ID must be atomic
        with self._lock:
            # NESTED CONTEXT: Transaction management
            with self._conn:
                # Execute INSERT statement and get a cursor object
                # Cursor is like a pointer to the result of the query
                #
                # SQL with PARAMETER BINDING:
                # - ? is a placeholder (prevents SQL injection attacks!)
                # - (original_url,) is a tuple of values to substitute for ?
                # - The comma after original_url makes it a tuple (not just parentheses)
                #
                # WHY USE PARAMETERIZED QUERIES?
                # - SECURITY: Prevents SQL injection (user can't insert malicious SQL)
                # - CORRECTNESS: Handles special characters in URLs automatically
                # - PERFORMANCE: Database can cache and reuse query plans
                #
                # SQL INJECTION EXAMPLE (DON'T DO THIS):
                # Bad:  "INSERT INTO urls VALUES ('" + url + "')"
                # If url is: '); DROP TABLE urls; --
                # Result: INSERT INTO urls VALUES (''); DROP TABLE urls; --')
                # This would delete your table!
                #
                # Good: Use ? placeholders - SQLite treats values as data, not code
                cursor = self._conn.execute(
                    "INSERT INTO url_mappings (original_url) VALUES (?)",
                    (original_url,),
                )
                
                # Get the ID of the row we just inserted
                # lastrowid is a cursor property that contains the auto-generated ID
                # Convert to int (it might be returned as a different type) and return
                #
                # SQLITE AUTO-INCREMENT:
                # - SQLite automatically assigns increasing integers: 1, 2, 3, ...
                # - PRIMARY KEY AUTOINCREMENT ensures IDs are never reused
                # - This ID is what we'll encode to create the short code
                return int(cursor.lastrowid)

    # ========================================================================
    # METHOD: update_short_hash
    # ========================================================================
    # Updates an existing record with its short code.
    # ========================================================================
    def update_short_hash(self, url_id: int, short_hash: str, original_url: str) -> None:
        """
        Update a URL record with its generated short code.
        
        Args:
            url_id: The unique ID of the record to update
            short_hash: The Base62 encoded short code (e.g., "abc123")
            original_url: The original URL (for consistency)
            
        Returns:
            None
            
        Thread Safety:
            Uses lock to ensure atomic UPDATE operation.
            
        SQL Operation:
            UPDATE url_mappings
            SET short_hash = 'abc123', original_url = 'https://example.com'
            WHERE id = 1
            
        Example:
            repo.update_short_hash(1, "abc123", "https://google.com")
            # Record 1 now has short_hash="abc123"
        """
        
        # CRITICAL SECTION: UPDATE must be atomic
        with self._lock:
            with self._conn:
                # Execute UPDATE statement with parameter binding
                # Updates the record identified by url_id
                #
                # SQL BREAKDOWN:
                # - UPDATE url_mappings: Modify records in url_mappings table
                # - SET short_hash = ?, original_url = ?: Set these fields to new values
                # - WHERE id = ?: Only update the record with this ID
                #
                # PARAMETERS:
                # - First ?: short_hash
                # - Second ?: original_url  
                # - Third ?: url_id
                # - Order matches the ?'s in the SQL string
                #
                # WHY UPDATE original_url AGAIN?
                # - We already saved it in save_and_get_id
                # - Updating again ensures consistency (in case it was modified)
                # - Could be optimized to only SET short_hash, but this is safer
                self._conn.execute(
                    """
                    UPDATE url_mappings
                    SET short_hash = ?, original_url = ?
                    WHERE id = ?
                    """,
                    (short_hash, original_url, url_id),
                )

    # ========================================================================
    # METHOD: get_original_url
    # ========================================================================
    # Looks up the original URL for a short code.
    # ========================================================================
    def get_original_url(self, short_hash: str) -> Optional[str]:
        """
        Retrieve the original URL for a short code.
        
        Args:
            short_hash: The short code to look up (e.g., "abc123")
            
        Returns:
            str: The original URL if found
            None: If the short code doesn't exist
            
        No lock needed:
            SELECT queries don't modify data, so concurrent reads are safe.
            SQLite handles read concurrency internally.
            
        SQL Operation:
            SELECT original_url FROM url_mappings WHERE short_hash = 'abc123'
            
        Example:
            url = repo.get_original_url("abc123")
            # Returns: "https://google.com" or None if not found
        """
        
        # Execute SELECT query and fetch one result
        # .fetchone() returns the first matching row, or None if no match
        #
        # SQL BREAKDOWN:
        # - SELECT original_url: Get only the original_url column (not all columns)
        # - FROM url_mappings: From this table
        # - WHERE short_hash = ?: Only rows where short_hash matches
        #
        # QUERY EXECUTION CHAIN:
        # 1. execute() sends SQL to database
        # 2. Database searches for matching short_hash
        # 3. fetchone() retrieves the first (and only) result
        # 4. Returns a Row object or None
        row = self._conn.execute(
            "SELECT original_url FROM url_mappings WHERE short_hash = ?",
            (short_hash,),
        ).fetchone()
        
        # Extract and return the original_url field
        # If row is None, the expression short-circuits and returns None
        # If row exists, convert row["original_url"] to string and return it
        #
        # TERNARY EXPRESSION: value_if_true if condition else value_if_false
        # row["original_url"]: Access the column by name (thanks to row_factory = Row)
        # str(...): Convert to string (SQLite might return different types)
        return str(row["original_url"]) if row else None

    # ========================================================================
    # METHOD: increment_click_count
    # ========================================================================
    # Increases the click counter for a short code.
    # ========================================================================
    def increment_click_count(self, short_hash: str) -> None:
        """
        Increment the click counter for a short code by 1.
        
        Args:
            short_hash: The short code being accessed
            
        Returns:
            None
            
        Thread Safety:
            Uses lock because UPDATE is a write operation.
            
        SQL Operation:
            UPDATE url_mappings
            SET click_count = click_count + 1
            WHERE short_hash = 'abc123'
            
        Example:
            repo.increment_click_count("abc123")
            # click_count in database goes from 5 to 6
        """
        
        # CRITICAL SECTION: UPDATE operation
        with self._lock:
            with self._conn:
                # Execute UPDATE statement to increment the counter
                #
                # SQL BREAKDOWN:
                # - UPDATE url_mappings: Modify records in this table
                # - SET click_count = click_count + 1: Add 1 to current value
                #   * This is ATOMIC in SQL - database handles the read-add-write
                #   * No race condition even with concurrent updates
                # - WHERE short_hash = ?: Only update this specific short code
                #
                # ATOMIC INCREMENT:
                # The database reads the current value, adds 1, and writes back
                # All in one atomic operation - no other query can interfere
                # This is safer than: read value → add 1 in Python → write back
                self._conn.execute(
                    """
                    UPDATE url_mappings
                    SET click_count = click_count + 1
                    WHERE short_hash = ?
                    """,
                    (short_hash,),
                )
                # Note: If short_hash doesn't exist, UPDATE affects 0 rows (silently ignored)
                # This matches the protocol contract (don't fail on missing keys)

    # ========================================================================
    # METHOD: get_all
    # ========================================================================
    # Returns all URL mappings (for admin/debug purposes).
    # ========================================================================
    def get_all(self) -> Dict[str, dict]:
        """
        Retrieve all stored URL mappings.
        
        Returns:
            Dict[str, dict]: Dictionary mapping short codes to URL records
                            Format: {
                                "abc123": {
                                    "url_id": 1,
                                    "original_url": "https://example.com",
                                    "click_count": 5
                                }
                            }
            
        SQL Operation:
            SELECT id, short_hash, original_url, click_count
            FROM url_mappings
            WHERE short_hash IS NOT NULL
            
        Example:
            all_urls = repo.get_all()
            # Returns: {"abc123": {...}, "def456": {...}}
        """
        
        # Execute SELECT query to get all complete URL records
        # .fetchall() returns a list of all matching rows
        #
        # SQL BREAKDOWN:
        # - SELECT id, short_hash, original_url, click_count: Get these columns
        # - FROM url_mappings: From this table
        # - WHERE short_hash IS NOT NULL: Only rows with a short_hash
        #   * Filters out incomplete records (URLs inserted but not yet encoded)
        #   * IS NOT NULL is the SQL way to check for non-NULL values
        rows = self._conn.execute(
            """
            SELECT id, short_hash, original_url, click_count
            FROM url_mappings
            WHERE short_hash IS NOT NULL
            """
        ).fetchall()
        
        # DICTIONARY COMPREHENSION: Build a dictionary from the query results
        # Syntax: {key_expression: value_expression for item in iterable}
        #
        # BREAKDOWN:
        # - for row in rows: Loop through each Row object returned by the query
        # - str(row["short_hash"]): Use short_hash as the dictionary key
        # - {...}: Create a nested dictionary with URL details as the value
        #
        # RESULT FORMAT:
        # {
        #     "abc123": {"url_id": 1, "original_url": "...", "click_count": 5},
        #     "def456": {"url_id": 2, "original_url": "...", "click_count": 3}
        # }
        #
        # This format matches MockUrlRepository.get_all() for consistency
        return {
            str(row["short_hash"]): {
                "url_id": int(row["id"]),
                "original_url": str(row["original_url"]),
                "click_count": int(row["click_count"]),
            }
            for row in rows
        }


# ============================================================================
# KEY OOP CONCEPTS DEMONSTRATED IN THIS FILE:
# ============================================================================
# 1. PROTOCOL / INTERFACE (UrlRepository)
#    - Defines a contract that implementations must follow
#    - Enables polymorphism - multiple implementations, same interface
#    - Allows dependency inversion - depend on abstraction, not concrete class
#
# 2. POLYMORPHISM (MockUrlRepository, SQLiteUrlRepository)
#    - Two different implementations of the same interface
#    - Can be used interchangeably
#    - Service layer doesn't know which one it's using
#
# 3. ENCAPSULATION
#    - All database/SQL logic is hidden inside repository classes
#    - Public methods provide simple interface
#    - Private methods (like _initialize_schema) hide implementation details
#    - Instance variables (like _conn, _lock) are internal
#
# 4. SINGLE RESPONSIBILITY PRINCIPLE
#    - MockUrlRepository: Only handles in-memory storage
#    - SQLiteUrlRepository: Only handles SQLite database operations
#    - Each class has ONE reason to change
#
# 5. DEPENDENCY INVERSION PRINCIPLE
#    - Service layer depends on UrlRepository (abstraction)
#    - Not on SQLiteUrlRepository or MockUrlRepository (concretions)
#    - High-level code doesn't depend on low-level implementation details
#
# 6. COMPOSITION
#    - Classes use Lock objects for thread safety
#    - SQLite class uses Connection object for database access
#    - "Has-a" relationships instead of "is-a" (inheritance)
#
# 7. THREAD SAFETY
#    - Both implementations use locks to prevent race conditions
#    - Critical sections are protected with 'with self._lock:'
#    - Safe for use in multi-threaded web server environment
#
# 8. REPOSITORY PATTERN
#    - Separates data access logic from business logic
#    - Provides collection-like interface for domain objects
#    - Makes it easy to swap data sources (SQLite → PostgreSQL → MongoDB)
#    - Improves testability (easy to mock)
# ============================================================================