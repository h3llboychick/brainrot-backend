from redis.asyncio import Redis

from src.domain.interfaces.repositories import IVerificationCodeRepository

from .verification_repository_settings import get_settings


class VerificationCodeRepository(IVerificationCodeRepository):
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.expiration_seconds = (
            get_settings().VERIFICATION_CODE_EXPIRATION_SECONDS
        )

    async def save(self, email: str, code: str) -> None:
        await self.redis_client.set(
            f"verification_code:{email}", code, ex=self.expiration_seconds
        )

    async def get_by_email(self, email: str) -> str | None:
        code = await self.redis_client.get(f"verification_code:{email}")
        return str(code, "utf-8") if code else None

    async def delete(self, email: str) -> None:
        await self.redis_client.delete(f"verification_code:{email}")
