from src.domain.entities.refresh_token import RefreshToken

from abc import ABC, abstractmethod


class ITokenRepository(ABC):
    @abstractmethod
    async def save_token(self, token: RefreshToken) -> None:
        """
        Save the token for the user.
        """
        pass

    @abstractmethod
    async def revoke_token(self, user_id: str, token: str) -> None:
        """
        Revoke the token for the user.
        """
        pass
    
    @abstractmethod
    async def is_token_active(self, token: str) -> bool:
        """
        Check if the token for the user is active.
        """
        pass