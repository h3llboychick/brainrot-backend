from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column("user_id", primary_key=True)
    balance: Mapped[float] = mapped_column(default=0.0, nullable=False)
    reserved_balance: Mapped[float] = mapped_column(default=0.0, nullable=False)
