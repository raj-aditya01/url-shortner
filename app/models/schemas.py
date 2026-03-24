# ============================================================================
# SCHEMAS.PY - DATA MODELS (REQUEST/RESPONSE STRUCTURES)
# ============================================================================
# This file defines the SHAPE of data that flows in and out of our API.
#
# WHAT IS PYDANTIC?
# - A library that validates data automatically
# - Ensures data has the correct type and format
# - Converts between Python objects and JSON
#
# WHY USE PYDANTIC MODELS?
# - VALIDATION: Automatically checks if data is valid
# - DOCUMENTATION: FastAPI uses these to generate API docs
# - TYPE SAFETY: Python knows what fields exist and their types
# - AUTO-CONVERSION: JSON → Python object → JSON automatically
#
# OOP CONCEPT: ENCAPSULATION
# - These classes bundle related data together
# - They define what data is allowed (schema)
# - They hide implementation details of validation
# ============================================================================

# IMPORTS
# ----------------------------------------------------------------------------
# BaseModel: The parent class all Pydantic models inherit from
# HttpUrl: A special type that validates URLs (checks format)
from pydantic import BaseModel, HttpUrl


# ============================================================================
# CLASS: URLCreateRequest
# ============================================================================
# This is a DATA MODEL class that represents an incoming HTTP request.
# When a user sends: POST /shorten with JSON body,
# FastAPI automatically converts the JSON to this Python object.
#
# OOP CONCEPT: INHERITANCE
# - URLCreateRequest inherits from BaseModel
# - This means it automatically gets all of BaseModel's features:
#   * Automatic JSON parsing
#   * Field validation
#   * Error messages
#   * Serialization/deserialization
#
# INHERITANCE SYNTAX: class Child(Parent):
# - URLCreateRequest is the CHILD/SUBCLASS
# - BaseModel is the PARENT/SUPERCLASS
# ============================================================================
class URLCreateRequest(BaseModel):
    """
    Request model: Represents the data sent when creating a short URL.
    
    This class defines what data the API expects when a user wants to shorten a URL.
    
    Attributes:
        original_url: The full URL that needs to be shortened
                      Type is HttpUrl, which means Pydantic will:
                      - Check if it's a valid URL format
                      - Ensure it has a scheme (http:// or https://)
                      - Reject invalid URLs like "not a url"
    
    Example JSON that would match this model:
        {
            "original_url": "https://www.example.com/very/long/path"
        }
    
    What happens when FastAPI receives this:
        1. FastAPI reads the JSON from the HTTP request body
        2. It creates a URLCreateRequest object
        3. Pydantic validates that original_url is a valid HTTP/HTTPS URL
        4. If valid: Creates the object and passes it to the route function
        5. If invalid: Returns a 422 error with details about what's wrong
    
    OOP CONCEPT: DATA ENCAPSULATION
    - The validation logic is hidden inside Pydantic
    - We just declare "this should be a URL" and Pydantic handles the rest
    """
    
    # CLASS ATTRIBUTE (also called INSTANCE ATTRIBUTE in Pydantic)
    # This defines a field that every instance of URLCreateRequest will have
    # The type annotation : HttpUrl tells Python and Pydantic the expected type
    original_url: HttpUrl


# ============================================================================
# CLASS: URLCreateResponse  
# ============================================================================
# This is a DATA MODEL class that represents an outgoing HTTP response.
# When our API creates a short URL, it returns this structure as JSON.
#
# OOP CONCEPT: INHERITANCE (again)
# - Also inherits from BaseModel
# - Gets automatic JSON conversion for responses
# ============================================================================
class URLCreateResponse(BaseModel):
    """
    Response model: Represents the data returned after creating a short URL.
    
    This class defines what data the API sends back to the user.
    
    Attributes:
        short_url: The complete shortened URL (e.g., "http://127.0.0.1:8000/abc123")
        original_url: The original long URL (echoed back for confirmation)
        
    Example JSON response:
        {
            "short_url": "http://127.0.0.1:8000/abc123",
            "original_url": "https://www.example.com/very/long/path"
        }
    
    What happens when our route returns this:
        1. The route function creates a URLCreateResponse object
        2. FastAPI uses Pydantic to convert it to JSON
        3. The JSON is sent as the HTTP response body
        4. The browser/client receives the JSON
    
    Why both fields are strings (str) instead of HttpUrl:
    - short_url: We build this ourselves, don't need validation
    - original_url: Already validated in the request, just echoing back
    
    OOP CONCEPT: SEPARATION OF CONCERNS
    - Request models handle INPUT validation
    - Response models handle OUTPUT formatting
    - Each class has a single, clear purpose
    """
    
    # These are simple string fields (no special validation)
    short_url: str        # Example: "http://127.0.0.1:8000/abc123"
    original_url: str     # Example: "https://www.example.com/very/long/path"


# ============================================================================
# KEY OOP CONCEPTS DEMONSTRATED HERE:
# ============================================================================
# 1. INHERITANCE: Both classes inherit from BaseModel
#    - They get all BaseModel features without reimplementing them
#    - This is CODE REUSE through inheritance
#
# 2. ENCAPSULATION: Validation logic is hidden
#    - We don't see HOW Pydantic validates URLs
#    - We just use the HttpUrl type and it works
#
# 3. ABSTRACTION: Simple interface for complex validation
#    - Just write: original_url: HttpUrl
#    - Pydantic handles all the validation complexity
#
# 4. TYPE SAFETY: Clear contracts for data
#    - Anyone reading this code knows exactly what data is expected
#    - IDEs can provide auto-completion
#    - Type checkers can catch errors before runtime
#
# 5. SINGLE RESPONSIBILITY: Each class has ONE job
#    - URLCreateRequest: Validate incoming data
#    - URLCreateResponse: Structure outgoing data
# ============================================================================
