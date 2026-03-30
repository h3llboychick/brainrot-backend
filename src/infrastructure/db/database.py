from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.infrastructure.db.settings import get_settings


class Database:
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None

    @property
    def is_initialized(self) -> bool:
        return self._engine is not None and self._sessionmaker is not None

    def init(self, url: str | None = None):
        if self.is_initialized:
            return
        db_url = url or get_settings().DB_URL
        self._engine = create_async_engine(db_url, echo=True)
        self._sessionmaker = async_sessionmaker(
            autocommit=False, bind=self._engine
        )

    async def close(self):
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        if not self.is_initialized:
            raise RuntimeError(
                "Database is not initialized. Call Database.init() first "
                "(this normally happens in the application lifespan)."
            )
        async with self._sessionmaker() as session:  # type: ignore
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()


db = Database()
