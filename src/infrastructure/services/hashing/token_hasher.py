from src.domain.interfaces.services.token_hasher import ITokenHasher

import hashlib


class SHA256TokenHasher(ITokenHasher):
    """
    Token hasher using SHA-256 algorithm.
    SHA-256 is fast and deterministic, suitable for token lookups in databases.
    """
    
    def hash_token(self, token: str) -> str:
        """Hash a token using SHA-256."""
        return hashlib.sha256(token.encode('utf-8')).hexdigest()


# Singleton instance
token_hasher = SHA256TokenHasher()
