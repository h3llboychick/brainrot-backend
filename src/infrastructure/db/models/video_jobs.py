from datetime import datetime
from typing import List
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.enums import VideoJobStatus
from src.infrastructure.db.models.base import Base
from src.infrastructure.db.models.video_formats import VideoFormat
from src.infrastructure.db.models.video_job_social_accounts import (
    VideoJobSocialAccount,
)


class VideoJob(Base):
    __tablename__ = "video_jobs"

    id: Mapped[str] = mapped_column(
        "video_job_id", default=lambda: str(uuid4()), primary_key=True
    )
    creator_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"), nullable=False
    )
    format_id: Mapped[int] = mapped_column(
        ForeignKey("video_formats.video_format_id"), nullable=False
    )
    status = mapped_column(PGEnum(VideoJobStatus), nullable=False)
    video_url: Mapped[str] = mapped_column(nullable=True, default=None)
    publish_automatically: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )
    scheduled_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    format: Mapped["VideoFormat"] = relationship()
    creator: Mapped["User"] = relationship(back_populates="video_jobs")  # noqa: F821, we can't import here due to circular import issues
    social_accounts: Mapped[List["VideoJobSocialAccount"]] = relationship(
        back_populates="video_job"
    )
