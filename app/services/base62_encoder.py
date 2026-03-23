class Base62Encoder:
    """Utility for converting integers to Base62 strings (0-9, a-z, A-Z)."""

    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

    @staticmethod
    def encode(num: int) -> str:
        """Convert an integer ID to a Base62 short code string."""
        if num == 0:
            return Base62Encoder.ALPHABET[0]

        base62_chars: list[str] = []
        base = len(Base62Encoder.ALPHABET)

        while num > 0:
            remainder = num % base
            base62_chars.append(Base62Encoder.ALPHABET[remainder])
            num //= base

        return "".join(reversed(base62_chars))