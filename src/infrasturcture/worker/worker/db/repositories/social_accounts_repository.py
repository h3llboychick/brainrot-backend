from ..models.social_account import SocialAccount as SocialAccountModel

from sqlalchemy.orm import Session
from sqlalchemy import select


class SocialAccountsRepository:
    def __init__(self, db_session: Session):
        self._db_session = db_session

    def get_social_account(self, user_id: str, platform: str) -> SocialAccountModel | None:
        return self._db_session.execute(
            select(SocialAccountModel).where(
                SocialAccountModel.owner_id == user_id,
                SocialAccountModel.platform == platform
            )
        ).scalar_one_or_none()