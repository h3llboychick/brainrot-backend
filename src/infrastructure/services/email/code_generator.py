from random import randint


def generate_verification_code() -> str:
    """Generate a random 6-digit verification code."""
    return str(randint(100000, 999999))