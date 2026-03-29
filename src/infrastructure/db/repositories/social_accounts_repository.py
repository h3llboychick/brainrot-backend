from src.domain.entities import SocialAccount
from src.domain.interfaces.repositories import ISocialAccountsRepository
from src.domain.enums import SocialPlatform

from src.infrastructure.db.models import SocialAccount as SocialAccountModel

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class SocialAccountsRepository(ISocialAccountsRepository):
    def __init__(self, db_session: AsyncSession):
        self._session = db_session

    async def save(self, social_account: SocialAccount) -> SocialAccount:
        social_account_model = SocialAccountModel(
            owner_id=social_account.owner_id,
            platform_account_id=social_account.platform_account_id,
            platform=social_account.platform,
            encrypted_credentials=social_account.encrypted_credentials,
            wrapped_dek=social_account.wrapped_dek,
            kek_id=social_account.kek_id,
        )
        self._session.add(social_account_model)
        await self._session.commit()
        await self._session.refresh(social_account_model)
        return SocialAccount.model_validate(social_account_model, from_attributes=True)

    async def list_by_owner(self, owner_id: str) -> list[SocialAccount]:
        result = await self._session.execute(
            select(SocialAccountModel).where(SocialAccountModel.owner_id == owner_id)
        )
        social_account_models = result.scalars().all()
        return [
            SocialAccount.model_validate(model, from_attributes=True)
            for model in social_account_models
        ]

    async def get_by_owner_and_platform_account_id(
        self, owner_id: str, platform: SocialPlatform, platform_account_id: str
    ) -> SocialAccount | None:
        social_account_model = (
            await self._session.execute(
                select(SocialAccountModel).where(
                    SocialAccountModel.owner_id == owner_id,
                    SocialAccountModel.platform == platform,
                    SocialAccountModel.platform_account_id == platform_account_id,
                )
            )
        ).scalar_one_or_none()

        return (
            SocialAccount.model_validate(social_account_model, from_attributes=True)
            if social_account_model
            else None
        )

    async def get_by_id(self, social_account_id: str) -> SocialAccount | None:
        social_account_model = (
            await self._session.execute(
                select(SocialAccountModel).where(
                    SocialAccountModel.id == social_account_id
                )
            )
        ).scalar_one_or_none()

        return (
            SocialAccount.model_validate(social_account_model, from_attributes=True)
            if social_account_model
            else None
        )

    async def update(self, social_account: SocialAccount) -> SocialAccount:
        social_account_model = await self._session.get(
            SocialAccountModel, social_account.id
        )
        if not social_account_model:
            raise ValueError("Social account not found for update.")

        social_account_model.encrypted_credentials = (
            social_account.encrypted_credentials
        )
        social_account_model.wrapped_dek = social_account.wrapped_dek
        social_account_model.kek_id = social_account.kek_id

        self._session.add(social_account_model)
        await self._session.commit()
        await self._session.refresh(social_account_model)
        return SocialAccount.model_validate(social_account_model, from_attributes=True)

    async def delete_by_id(self, social_account_id: str) -> None:
        social_account_model = await self._session.get(
            SocialAccountModel, social_account_id
        )
        if social_account_model:
            await self._session.delete(social_account_model)
            await self._session.commit()
