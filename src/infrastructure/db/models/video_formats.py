from src.infrastructure.db.models.base import Base

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import mapped_column, Mapped


class VideoFormat(Base):
    __tablename__ = "video_formats"

    id: Mapped[int] = mapped_column(
        "video_format_id", primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    description: Mapped[str] = mapped_column(nullable=True)
    price: Mapped[float] = mapped_column(nullable=False)

    __table_args__ = (CheckConstraint("price >= 0", name="check_price_non_negative"),)
