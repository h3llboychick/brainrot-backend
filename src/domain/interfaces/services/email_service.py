from src.domain.dtos.auth.verification import EmailVerificationDTO

from abc import ABC, abstractmethod


class IEmailService(ABC):
    @abstractmethod
    async def send_verification_email(self, payload: EmailVerificationDTO) -> None:
        """Send a confirmation email to the user."""
        pass
