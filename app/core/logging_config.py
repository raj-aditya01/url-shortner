# ============================================================================
# LOGGING_CONFIG.PY - APPLICATION LOGGING CONFIGURATION
# ============================================================================
# This file sets up logging for the entire application.
#
# WHAT IS LOGGING?
# - Recording events that happen during program execution
# - Like a diary for your application
# - Helps with debugging, monitoring, and troubleshooting
#
# WHY USE LOGGING INSTEAD OF PRINT?
# - LEVELS: Info, Warning, Error - filter by severity
# - FORMATTING: Consistent format with timestamps, module names
# - FLEXIBILITY: Easy to redirect output (file, console, remote server)
# - PERFORMANCE: Can be disabled in production for sensitive data
# - FILTERING: Can show logs from specific modules only
#
# LOGGING LEVELS (from least to most severe):
# - DEBUG: Detailed information for diagnosing problems
# - INFO: Confirmation that things are working as expected
# - WARNING: Something unexpected, but program continues
# - ERROR: Serious problem, program function is impaired
# - CRITICAL: Very serious, program might not be able to continue
#
# EXAMPLE LOGS FROM OUR APPLICATION:
# - INFO: "Created short URL abc123 for https://google.com"
# - INFO: "Redirecting abc123 to https://google.com"  
# - WARNING: "Short hash not found: xyz789"
# ============================================================================

# IMPORTS
# ----------------------------------------------------------------------------
# logging: Python's built-in logging library
# Provides a standardized way to emit log messages
import logging


# ============================================================================
# FUNCTION: setup_logging
# ============================================================================
# Configures the logging system for the entire application.
# Called once at startup (in main.py).
#
# After calling this function, any module can use logging:
#   import logging
#   logger = logging.getLogger(__name__)
#   logger.info("Hello world!")
# ============================================================================
def setup_logging() -> None:
    """
    Configure logging for the entire application.
    
    Sets up logging with a consistent format across all modules.
    This function should be called once when the application starts.
    
    Configuration:
        - Level: INFO (shows INFO, WARNING, ERROR, CRITICAL - hides DEBUG)
        - Format: "timestamp level [module_name] message"
        - Output: Console/terminal (stderr)
        
    Example output:
        2026-03-24 10:15:43 INFO [app.api.routes.url_routes] Created short URL abc123 for https://google.com
        2026-03-24 10:15:44 INFO [app.api.routes.url_routes] Redirecting abc123 to https://google.com
        2026-03-24 10:15:45 WARNING [app.api.routes.url_routes] Short hash not found: xyz789
    
    Returns:
        None (this function configures logging but doesn't return anything)
        
    Usage:
        # In main.py (called once at startup)
        setup_logging()
        
        # In any other file (after setup_logging() has been called)
        import logging
        logger = logging.getLogger(__name__)
        logger.info("This is an informational message")
        logger.warning("This is a warning")
        logger.error("This is an error")
        
    OOP CONCEPT: CONFIGURATION FUNCTION
        - This is a UTILITY FUNCTION, not a method
        - It configures a SINGLETON (the root logger)
        - After configuration, all loggers in all modules share this config
        - This is the FACADE PATTERN - simple interface for complex system
    """
    
    # Call logging.basicConfig() to configure the root logger
    # The root logger is the parent of all other loggers in the application
    # Any logger created with logging.getLogger() will inherit this configuration
    #
    # PARAMETERS:
    # - level: The minimum level to log (INFO means INFO and above)
    # - format: The format string for log messages
    #
    # basicConfig() can only be called once (subsequent calls are ignored)
    # So we call it early in main.py before any logging happens
    logging.basicConfig(
        # SET LOGGING LEVEL: logging.INFO
        # This means: Show INFO, WARNING, ERROR, CRITICAL messages
        # Hide DEBUG messages (too detailed for normal operation)
        #
        # To change level:
        # - logging.DEBUG: Show everything (very verbose)
        # - logging.INFO: Normal operation (default)
        # - logging.WARNING: Only show warnings and errors
        # - logging.ERROR: Only show errors and critical issues
        #
        # In production, you might use WARNING or ERROR to reduce noise
        # In development, INFO or DEBUG for more detail
        level=logging.INFO,
        
        # SET LOG MESSAGE FORMAT
        # This controls what each log message looks like
        #
        # FORMAT STRING PLACEHOLDERS:
        # - %(asctime)s: Timestamp when the log message was created
        #   Example: "2026-03-24 10:15:43,123"
        #   's' means convert to string
        #
        # - %(levelname)s: Severity level of the message
        #   Example: "INFO", "WARNING", "ERROR"
        #   's' means convert to string
        #
        # - %(name)s: Name of the logger (usually the module name)
        #   Example: "app.api.routes.url_routes"
        #   Helps identify which part of the code logged the message
        #   's' means convert to string
        #
        # - %(message)s: The actual log message
        #   Example: "Created short URL abc123 for https://google.com"
        #   's' means convert to string
        #
        # EXAMPLE OUTPUT:
        # "2026-03-24 10:15:43,123 INFO [app.api.routes.url_routes] Created short URL abc123"
        #
        # FORMAT BREAKDOWN:
        # - Timestamp: Helps with chronological debugging
        # - Level: Quickly see severity (scan for ERROR or WARNING)
        # - [Module name]: Know which file/component logged it
        # - Message: The actual information
        #
        # This format is a good balance between readability and information
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    
    # After this function completes, logging is configured!
    # Any module can now create a logger and start logging:
    #
    # import logging
    # logger = logging.getLogger(__name__)  # __name__ is the module name
    # logger.info("Application started")   # Outputs: "timestamp INFO [module] Application started"
    # logger.warning("Low disk space")     # Outputs: "timestamp WARNING [module] Low disk space"
    # logger.error("Database error")       # Outputs: "timestamp ERROR [module] Database error"
    # logger.debug("Variable x = 5")       # Hidden (because level=INFO, DEBUG is below INFO)


# ============================================================================
# KEY CONCEPTS DEMONSTRATED HERE:
# ============================================================================
# 1. CENTRALIZED CONFIGURATION
#    - All logging configuration in one place
#    - Easy to change format or level for entire application
#    - No need to configure logging in every module
#
# 2. SINGLETON PATTERN
#    - The root logger is a singleton (only one instance)
#    - All other loggers inherit from it
#    - Configuration applies to the whole application
#
# 3. FACADE PATTERN
#    - setup_logging() provides a simple interface
#    - Hides the complexity of logging.basicConfig()
#    - Other code just calls setup_logging() and it works
#
# 4. SEPARATION OF CONCERNS
#    - Logging configuration is separate from business logic
#    - Easy to modify without touching other code
#    - Can be extended (add file handlers, remote logging, etc.)
#
# 5. REUSABILITY
#    - Any module can create a logger with logging.getLogger()
#    - All use the same configuration (consistent formatting)
#    - No need to pass logger objects around
#
# 6. OBSERVABILITY
#    - Logging provides visibility into application behavior
#    - Essential for debugging production issues
#    - Can be integrated with monitoring tools (ELK, Splunk, etc.)
# ============================================================================
