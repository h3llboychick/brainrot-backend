from src.domain.interfaces.repositories.token_respository import ITokenRepository
from src.domain.interfaces.services.token_hasher import ITokenHasher
from src.domain.entities.refresh_token import RefreshToken
from src.domain.exceptions.tokens import TokenNotFoundError, TokenAlreadyRevokedError

from src.infrastructure.db.models.refresh_tokens import RefreshToken as RefreshTokenModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class TokenRepository(ITokenRepository):
    def __init__(self, db_session: AsyncSession, token_hasher: ITokenHasher):
        self.db_session = db_session
        self.token_hasher = token_hasher
    async def save_token(self, token: RefreshToken) -> None:
        token_model = RefreshTokenModel(
            user_id=token.user_id,
            hashed_token=self.token_hasher.hash_token(token.token),
            expires_at=token.expires_at,
            created_at=token.created_at
        )
        self.db_session.add(token_model)
        await self.db_session.commit()

    async def revoke_token(self, user_id: str, token: str) -> None:
        query = select(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id, RefreshTokenModel.hashed_token == self.token_hasher.hash_token(token))
        token_model: RefreshTokenModel | None = (await self.db_session.execute(query)).scalar_one_or_none()

        if not token_model:
            raise TokenNotFoundError()
        
        if token_model.revoked:
            raise TokenAlreadyRevokedError()

        token_model.revoked = True
        await self.db_session.commit()
    
    async def is_token_active(self, token: str) -> bool:
        query = select(RefreshToken).where(RefreshToken.hashed_token == self.token_hasher.hash_token(token))
        token_model: RefreshToken | None = (await self.db_session.execute(query)).scalar_one_or_none()

        if not token_model:
            raise TokenNotFoundError()
        return not token_model.revoked