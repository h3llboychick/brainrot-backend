from datetime import datetime

from pydantic import BaseModel

from src.domain.entities.video_format import VideoFormat
from src.domain.enums import UserRole


class User(BaseModel):
    id: str | None = None
    email: str
    hashed_password: str | None = None
    google_id: str | None = None
    is_active: bool = True
    is_verified: bool = False
    balance: float = 0.0
    role: UserRole = UserRole.user
    created_at: datetime

    def is_admin(self) -> bool:
        return self.role == "admin"

    def can_generate_video(self, video_format: VideoFormat) -> bool:
        return self.balance >= video_format.price

    def deduct_balance(self, amount: float) -> None:
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        self.balance -= amount

    def add_balance(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Cannot add negative balance")
        self.balance += amount
