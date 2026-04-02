from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class VideoJob(Base):
    __tablename__ = "video_jobs"

    id: Mapped[str] = mapped_column("video_job_id", primary_key=True)
    status: Mapped[str] = mapped_column(nullable=False)
