from abc import ABC, abstractmethod

from src.domain.entities import RefreshToken


class ITokenRepository(ABC):
    @abstractmethod
    async def save(self, token: RefreshToken) -> None:
        """
        Save the token for the user.
        """
        pass

    @abstractmethod
    async def revoke(self, user_id: str, token: str) -> None:
        """
        Revoke the token for the user.
        """
        pass

    @abstractmethod
    async def is_active(self, token: str) -> bool:
        """
        Check if the token for the user is active.
        """
        pass
