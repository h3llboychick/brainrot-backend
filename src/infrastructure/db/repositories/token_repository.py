from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import RefreshToken
from src.domain.exceptions import TokenAlreadyRevokedError, TokenNotFoundError
from src.domain.interfaces.repositories import ITokenRepository
from src.domain.interfaces.services import ITokenHasher
from src.infrastructure.db.models import RefreshToken as RefreshTokenModel


class TokenRepository(ITokenRepository):
    def __init__(self, db_session: AsyncSession, token_hasher: ITokenHasher):
        self.db_session = db_session
        self.token_hasher = token_hasher

    async def save(self, token: RefreshToken) -> None:
        token_model = RefreshTokenModel(
            user_id=token.user_id,
            hashed_token=self.token_hasher.hash_token(token.token),
            expires_at=token.expires_at,
            created_at=token.created_at,
        )
        self.db_session.add(token_model)
        await self.db_session.commit()

    async def revoke(self, user_id: str, token: str) -> None:
        query = select(RefreshTokenModel).where(
            RefreshTokenModel.user_id == user_id,
            RefreshTokenModel.hashed_token
            == self.token_hasher.hash_token(token),
        )
        token_model: RefreshTokenModel | None = (
            await self.db_session.execute(query)
        ).scalar_one_or_none()

        if not token_model:
            raise TokenNotFoundError()

        if token_model.revoked:
            raise TokenAlreadyRevokedError()

        token_model.revoked = True
        await self.db_session.commit()

    async def is_active(self, token: str) -> bool:
        query = select(RefreshTokenModel).where(
            RefreshTokenModel.hashed_token
            == self.token_hasher.hash_token(token)
        )
        token_model: RefreshTokenModel | None = (
            await self.db_session.execute(query)
        ).scalar_one_or_none()

        if not token_model:
            raise TokenNotFoundError()
        return not token_model.revoked
