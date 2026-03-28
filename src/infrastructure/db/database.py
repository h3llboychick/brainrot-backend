from src.infrastructure.db.settings import settings

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)


engine = None
sessionmaker = None


def init_db():
    global sessionmaker, engine
    if not (sessionmaker and engine):
        engine = create_async_engine(
            settings.DB_URL,
            echo=True,
        )
        sessionmaker = async_sessionmaker(autocommit=False, bind=engine)


async def close_db():
    global sessionmaker, engine
    if engine:
        await engine.dispose()
        engine = None
        sessionmaker = None


# This function provides an AsyncSesssion object that can be used in FastAPI dependencies
# It uses the sessionmanager to create a new session and yields it for use in the request
# See https://stackoverflow.com/questions/34322471/sqlalchemy-engine-connection-and-session-difference to understand the difference between engine, connection, and session
async def get_db_session():
    global sessionmaker
    async with sessionmaker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
