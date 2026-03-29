from abc import ABC, abstractmethod


class IVerificationCodeRepository(ABC):
    @abstractmethod
    async def save(self, email: str, code: str) -> None:
        """Save the verification code for the user."""
        pass

    @abstractmethod
    async def get_by_email(self, email: str) -> str | None:
        """Retrieve the verification code for the user."""
        pass

    @abstractmethod
    async def delete(self, email: str) -> None:
        """Delete the verification code for the user."""
        pass
