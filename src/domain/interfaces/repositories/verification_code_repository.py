from abc import ABC, abstractmethod


class IVerificationCodeRepository(ABC):
    @abstractmethod
    async def save_code(self, email: str, code: str) -> None:
        """Save the verification code for the user."""
        pass
    @abstractmethod
    async def get_code(self, email: str) -> str:
        """Retrieve the verification code for the user."""
        pass
    @abstractmethod
    async def delete_code(self, email: str) -> None:
        """Delete the verification code for the user."""
        pass
