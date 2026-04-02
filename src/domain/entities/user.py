from datetime import datetime

from pydantic import BaseModel

from src.domain.entities.video_format import VideoFormat
from src.domain.enums import UserRole
from src.domain.exceptions.users import InsufficientBalanceError


class User(BaseModel):
    id: str | None = None
    email: str
    hashed_password: str | None = None
    google_id: str | None = None
    is_active: bool = True
    is_verified: bool = False
    balance: float = 0.0
    reserved_balance: float = 0.0
    role: UserRole = UserRole.user
    created_at: datetime

    def is_admin(self) -> bool:
        return self.role == "admin"

    @property
    def available_balance(self) -> float:
        """Balance available for new reservations (excludes held funds)."""
        return self.balance - self.reserved_balance

    def can_generate_video(self, video_format: VideoFormat) -> bool:
        return self.available_balance >= video_format.price

    def reserve_balance(self, amount: float) -> None:
        """Hold funds for a pending job. Moves amount into reserved_balance."""
        if amount <= 0:
            raise ValueError("Reservation amount must be positive")
        if amount > self.available_balance:
            raise InsufficientBalanceError(
                "Insufficient balance for reservation"
            )
        self.reserved_balance += amount

    def confirm_reservation(self, amount: float) -> None:
        """Finalize a charge: deduct from both balance and reserved_balance."""
        if amount <= 0:
            raise ValueError("Confirmation amount must be positive")
        if amount > self.reserved_balance:
            raise ValueError("Confirmation amount exceeds reserved balance")
        self.balance -= amount
        self.reserved_balance -= amount

    def release_reservation(self, amount: float) -> None:
        """Release held funds back to available balance."""
        if amount <= 0:
            raise ValueError("Release amount must be positive")
        if amount > self.reserved_balance:
            raise ValueError("Release amount exceeds reserved balance")
        self.reserved_balance -= amount

    def deduct_balance(self, amount: float) -> None:
        if amount > self.balance:
            raise InsufficientBalanceError("Insufficient balance")
        self.balance -= amount

    def add_balance(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("Cannot add negative balance")
        self.balance += amount
