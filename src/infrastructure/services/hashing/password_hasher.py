from passlib.context import CryptContext

from src.domain.interfaces.services import IPasswordHasher


class BcryptPasswordHasher(IPasswordHasher):
    """
    Password hasher using bcrypt algorithm.
    Bcrypt is specifically designed for password hashing - it's slow and uses salts.
    """

    def __init__(self, context: CryptContext | None = None):
        self.context = context or CryptContext(
            schemes=["bcrypt"], deprecated="auto"
        )

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return self.context.hash(password)

    def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        """Verify a plain password against a bcrypt hashed password."""
        return self.context.verify(plain_password, hashed_password)


# Singleton instance
password_hasher = BcryptPasswordHasher()
