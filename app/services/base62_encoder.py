# ============================================================================
# BASE62_ENCODER.PY - NUMBER TO SHORT CODE CONVERTER
# ============================================================================
# This file converts large numbers into short, URL-friendly codes.
#
# WHAT IS BASE62 ENCODING?
# - Similar to how we count in Base10 (0-9) or Base16/Hexadecimal (0-9, A-F)
# - Base62 uses: 0-9 (10 digits) + a-z (26 letters) + A-Z (26 letters) = 62 characters
# - Allows representing big numbers with fewer characters
#
# EXAMPLE CONVERSIONS:
# - Number 0 → "0"
# - Number 61 → "Z" 
# - Number 62 → "10"
# - Number 1000001 → "4c93"
#
# WHY USE BASE62?
# - SHORTER URLS: 1000001 (7 characters) becomes "4c93" (4 characters)
# - URL-SAFE: Only uses characters allowed in URLs (no special symbols)
# - UNIQUE: Each number maps to exactly one Base62 string
# - REVERSIBLE: You can decode "4c93" back to 1000001 (though we don't do that here)
#
# OOP CONCEPT: UTILITY CLASS
# - This class groups related functions together
# - All methods are static (don't need an instance to use them)
# - It's like a toolbox of related helper functions
# ============================================================================


# ============================================================================
# CLASS: Base62Encoder
# ============================================================================
# This is a UTILITY CLASS - it provides helper functions but doesn't store data.
# 
# OOP CONCEPT: STATIC METHODS
# - Methods that belong to the class, not to instances
# - You call them like: Base62Encoder.encode(123)
# - You DON'T create an instance: encoder = Base62Encoder()  # Not needed!
#
# WHY USE A CLASS FOR THIS?
# - ORGANIZATION: Groups related functions together
# - NAMESPACE: Avoids name conflicts (encode could be used elsewhere)
# - CLARITY: Makes it clear these functions are related to Base62 encoding
# ============================================================================
class Base62Encoder:
    """
    Utility class for converting integers to Base62 strings.
    
    Base62 uses 62 characters: 0-9, a-z, A-Z
    This creates short, URL-friendly codes from database IDs.
    
    Example usage:
        short_code = Base62Encoder.encode(1000001)  # Returns "4c93"
        
    You don't create an instance:
        encoder = Base62Encoder()  # Not needed!
        Just call the static method directly on the class name.
    """

    # ========================================================================
    # CLASS CONSTANT: ALPHABET
    # ========================================================================
    # This defines the 62 characters we use for encoding.
    # Position 0 = '0', Position 1 = '1', ..., Position 61 = 'Z'
    #
    # WHY ALL CAPS?
    # - Python convention: ALL_CAPS indicates a constant (value never changes)
    #
    # WHY THIS ORDER?
    # - 0-9 first: Makes small numbers look like normal numbers
    # - a-z next: Lowercase letters
    # - A-Z last: Uppercase letters
    # - This specific order is a common Base62 standard
    # ========================================================================
    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    # ========================================================================
    # STATIC METHOD: encode
    # ========================================================================
    # The @staticmethod decorator tells Python this method doesn't need 'self'
    # It belongs to the class, not to instances
    #
    # PARAMETERS:
    #   num (int): The number to convert (usually a database ID like 1000001)
    #
    # RETURNS:
    #   str: The Base62 encoded string (like "4c93")
    # ========================================================================
    @staticmethod
    def encode(num: int) -> str:
        """
        Convert an integer ID to a Base62 short code string.
        
        This is the core algorithm that makes URL shortening work!
        
        Args:
            num: The integer to encode (e.g., database ID: 1000001)
            
        Returns:
            str: The Base62 encoded string (e.g., "4c93")
            
        Algorithm Explanation:
            Base62 encoding works like converting between number systems.
            
            Think about how Base10 works:
            - The number 456 means: 4×10² + 5×10¹ + 6×10⁰
            
            Base62 is similar but uses 62 instead of 10:
            - We repeatedly divide by 62 and collect the remainders
            - Each remainder becomes a character in our ALPHABET
            
        Example step-by-step for num=125:
            Step 1: 125 ÷ 62 = 2 remainder 1  → ALPHABET[1] = '1'
            Step 2: 2 ÷ 62 = 0 remainder 2    → ALPHABET[2] = '2'
            Result: "21" (reversed order)
            
        Why reverse?
        - We collect remainders from right to left (least significant first)
        - But we want to write them left to right (most significant first)
        - So we reverse at the end
        """
        
        # SPECIAL CASE: Zero
        # If the input is 0, return the first character in our alphabet ('0')
        # Without this check, the while loop below wouldn't run for 0
        if num == 0:
            return Base62Encoder.ALPHABET[0]

        # STEP 1: Create an empty list to store Base62 characters
        # We use a list because it's efficient to append to
        # Later we'll join these characters into a string
        base62_chars: list[str] = []
        
        # STEP 2: Store the base (62) to avoid recalculating
        # len(ALPHABET) = 62 (number of characters in our alphabet)
        base = len(Base62Encoder.ALPHABET)

        # STEP 3: Convert to Base62 using division and remainder
        # This loop runs until we've processed all digits
        # Each iteration processes one Base62 "digit"
        while num > 0:
            # Calculate remainder when dividing by 62
            # This gives us which character to use (0-61)
            # Example: 125 % 62 = 1
            remainder = num % base
            
            # Look up the character at that position in our ALPHABET
            # Example: ALPHABET[1] = '1'
            # Add it to our list of characters
            base62_chars.append(Base62Encoder.ALPHABET[remainder])
            
            # Integer division: divide by 62 and discard the remainder
            # This moves to the next "digit" position
            # Example: 125 // 62 = 2
            # // is integer division (5 // 2 = 2, not 2.5)
            num //= base

        # STEP 4: Reverse and join the characters
        # Why reverse?
        # - We built the string backwards (least significant digit first)
        # - reversed() flips the order
        # - "".join() combines the list into a single string
        # Example: ['1', '2'] → reversed → ['2', '1'] → "21"
        return "".join(reversed(base62_chars))


# ============================================================================
# KEY OOP CONCEPTS DEMONSTRATED HERE:
# ============================================================================
# 1. UTILITY CLASS: Groups related helper functions
#    - Base62Encoder is a container for encoding functions
#    - Could add decode() method later in the same class
#
# 2. STATIC METHODS: Functions that don't need object state
#    - encode() doesn't need any instance data
#    - Can be called directly on the class
#    - Alternative: Could be a standalone function, but grouping in a class is cleaner
#
# 3. CLASS CONSTANTS: Data that belongs to the class, not instances
#    - ALPHABET is shared by all uses of Base62Encoder
#    - Never changes, so it's a constant
#
# 4. SINGLE RESPONSIBILITY: This class does ONE thing
#    - Converts numbers to Base62 strings
#    - Doesn't handle URLs, databases, or HTTP
#    - Easy to understand, test, and reuse
#
# 5. ALGORITHM ENCAPSULATION: Complex logic hidden behind simple interface
#    - Users just call encode(num) and get a result
#    - They don't need to understand the Base62 algorithm
#    - Implementation can be changed without affecting users
# ============================================================================