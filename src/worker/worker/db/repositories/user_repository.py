from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.user import User


class UserRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, user_id: str) -> User | None:
        return self._session.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()

    def get_by_id_for_update(self, user_id: str) -> User | None:
        """Load user with a row-level lock for safe balance updates."""
        return self._session.execute(
            select(User).where(User.id == user_id).with_for_update()
        ).scalar_one_or_none()
