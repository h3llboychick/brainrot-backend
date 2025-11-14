from src.infrastructure.db.settings import settings

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    async_sessionmaker,
    create_async_engine,
    AsyncSession
)

import contextlib
from typing import AsyncIterator, Any


class DatabaseSessionManager:
    def __init__(self, db_url: str, engine_kwargs: dict[str, Any] = {}):
        # Initializing engine and sessionmaker objects
        self._engine = create_async_engine(db_url, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine)

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

sessionmanager = DatabaseSessionManager(settings.DB_URL, {"echo": False})

# This function provides an AsyncSesssion object that can be used in FastAPI dependencies
# It uses the sessionmanager to create a new session and yields it for use in the request
# See https://stackoverflow.com/questions/34322471/sqlalchemy-engine-connection-and-session-difference to understand the difference between engine, connection, and session
async def get_db_session():
    async with sessionmanager.session() as session:
        yield session

