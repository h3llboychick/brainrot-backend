from src.domain.dtos.auth import EmailVerificationDTO

from abc import ABC, abstractmethod


class IEmailService(ABC):
    @abstractmethod
    def send_verification_email(self, payload: EmailVerificationDTO) -> None:
        """Send a confirmation email to the user."""
        pass
