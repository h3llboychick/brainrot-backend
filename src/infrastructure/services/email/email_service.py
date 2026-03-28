from src.domain.interfaces.services import IEmailService
from src.domain.dtos.auth import EmailVerificationDTO

from .settings import settings

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from fastapi import BackgroundTasks


class EmailService(IEmailService):
    def __init__(self, background_tasks: BackgroundTasks):
        self.conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=settings.USE_CREDENTIALS,
            VALIDATE_CERTS=settings.VALIDATE_CERTS,
            TEMPLATE_FOLDER=settings.HTML_TEMPLATE_DIR,
        )
        self.background_tasks = background_tasks

    def send_verification_email(self, payload: EmailVerificationDTO):
        message = MessageSchema(
            subject="Email Verification",
            recipients=[payload.email],
            template_body={
                "verification_code": payload.verification_code,
                "user_name": payload.email,
            },
            subtype="html",
        )

        fm = FastMail(self.conf)
        self.background_tasks.add_task(
            fm.send_message, message, template_name="email_verification.html"
        )
