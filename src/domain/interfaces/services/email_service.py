from abc import ABC, abstractmethod

from src.domain.dtos.auth import EmailVerificationDTO


class IEmailService(ABC):
    @abstractmethod
    def send_verification_email(self, payload: EmailVerificationDTO) -> None:
        """Send a confirmation email to the user."""
        pass
