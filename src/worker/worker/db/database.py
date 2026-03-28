from ..settings import settings

from sqlalchemy import create_engine, Connection
from sqlalchemy.orm import sessionmaker, Session

import contextlib
from typing import Iterator, Any


class DatabaseSessionManager:
    def __init__(self, db_url: str, engine_kwargs: dict[str, Any] = {}):
        # Initializing engine and sessionmaker objects
        self._engine = create_engine(db_url, **engine_kwargs)
        self._sessionmaker = sessionmaker(autocommit=False, bind=self._engine)

    def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.contextmanager
    def connect(self) -> Iterator[Connection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                connection.rollback()
                raise

    @contextlib.contextmanager
    def session(self) -> Iterator[Session]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


sessionmanager = DatabaseSessionManager(settings.DB_URL, {"echo": False})
