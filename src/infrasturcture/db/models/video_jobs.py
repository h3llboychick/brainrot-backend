from src.domain.enums.video_job_status import VideoJobStatus

from src.infrasturcture.db.models.video_formats import VideoFormat
from src.infrasturcture.db.models.video_job_social_accounts import VideoJobSocialAccount
from src.infrasturcture.db.models.base import Base

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import ENUM as PGEnum

from uuid import uuid4
from datetime import datetime
from typing import List


class VideoJob(Base):
    __tablename__ = "video_jobs"
    
    id: Mapped[str] = mapped_column("video_job_id", default=str(uuid4()), primary_key=True)
    creator_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    format_id: Mapped[int] = mapped_column(ForeignKey("video_formats.video_format_id"), nullable=False)
    status = mapped_column(PGEnum(VideoJobStatus), nullable=False)
    video_url: Mapped[str] = mapped_column(nullable=True, default=None)
    publish_automatically: Mapped[bool] = mapped_column(default=False, nullable=False)
    scheduled_at: Mapped[datetime] = mapped_column(nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    published_at: Mapped[datetime] = mapped_column(nullable=True, default=None)
    
    format: Mapped["VideoFormat"] = relationship()
    creator: Mapped["User"] = relationship(back_populates="video_jobs")
    social_accounts: Mapped[List["VideoJobSocialAccount"]] = relationship(
        back_populates="video_job"
    )