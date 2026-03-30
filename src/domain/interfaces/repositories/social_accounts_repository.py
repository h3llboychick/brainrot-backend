from abc import ABC, abstractmethod

from src.domain.entities import SocialAccount
from src.domain.enums import SocialPlatform


class ISocialAccountsRepository(ABC):
    @abstractmethod
    async def save(self, social_account: SocialAccount) -> SocialAccount:
        pass

    @abstractmethod
    async def list_by_owner(self, owner_id: str) -> list[SocialAccount]:
        pass

    @abstractmethod
    async def get_by_owner_and_platform_account_id(
        self, owner_id: str, platform: SocialPlatform, platform_account_id: str
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
