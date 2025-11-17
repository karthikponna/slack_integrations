import string
import random


def generate_random_hex(length: int) -> str:
    """Generate a random hexadecimal string of specified length.
    
    Args:
        length: Number of hexadecimal characters to generate.
    
    Returns:
        str: Random lowercase hexadecimal string.
    """
    
    hex_chars = string.hexdigits.lower()
    return "".join(random.choice(hex_chars) for _ in range(length))
