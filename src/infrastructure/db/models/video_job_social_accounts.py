from src.infrasturcture.db.models.base import Base
from src.infrasturcture.db.models.social_accounts import SocialAccount

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship


class VideoJobSocialAccount(Base):
    __tablename__ = "video_job_social_account"

    video_job_id: Mapped[str] = mapped_column(ForeignKey("video_jobs.video_job_id"), primary_key=True, nullable=False)
    social_account_id: Mapped[str] = mapped_column(ForeignKey("social_accounts.social_account_id"), primary_key=True, nullable=False)

    video_job: Mapped["VideoJob"] = relationship()
    social_account: Mapped["SocialAccount"] = relationship()
    
    