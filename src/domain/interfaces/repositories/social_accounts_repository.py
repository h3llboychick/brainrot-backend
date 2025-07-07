from src.domain.entities.social_account import SocialAccount

from abc import ABC, abstractmethod


class ISocialAccountsRepository(ABC):
    @abstractmethod
    async def create(self, social_account: SocialAccount) -> SocialAccount:
        pass
    
    @abstractmethod
    async def list_by_owner(self, owner_id: str) -> list[SocialAccount]:
        pass
    
    @abstractmethod
    async def get_by_owner_and_platform_account_id(
        self,
        owner_id: str,
        platform: str,
        platform_account_id: str
    ) -> SocialAccount | None:
        pass
    
    @abstractmethod
    async def get_by_id(self, social_account_id: str) -> SocialAccount | None:
        pass
    
    @abstractmethod
    async def update(self, social_account: SocialAccount) -> SocialAccount:
        pass
    
    @abstractmethod
    async def delete_by_id(self, social_account_id: str) -> None:
        pass
