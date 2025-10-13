import string
import random


def generate_random_hex(length: int) -> str:

    hex_chars = string.hexdigits.lower()
    return "".join(random.choice(hex_chars) for _ in range(length))
