from src.domain.enums.user_role import UserRole

from src.infrastructure.db.models.video_jobs import VideoJob
from src.infrastructure.db.models.base import Base

from sqlalchemy import func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import ENUM as PGEnum

from datetime import datetime
from typing import List
from uuid import uuid4


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column("user_id", default=str(uuid4()), primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=True)
    google_id: Mapped[str] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(default=False, nullable=False)
    balance: Mapped[float] = mapped_column(default=0.0, nullable=False)
    role = mapped_column(PGEnum(UserRole), default=UserRole.user, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)   
    
    video_jobs: Mapped[List["VideoJob"]] = relationship(back_populates="creator")
    social_accounts: Mapped[List["SocialAccount"]] = relationship(
        back_populates="owner"
    )