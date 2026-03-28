from src.domain.interfaces.services import (
    IVideoProcessor,
    ITokenService,
    ICredentialsProtector,
    IPasswordHasher,
    IEmailService,
    ITokenHasher,
)


from src.infrastructure.services.video_processing import video_processor
from src.infrastructure.services.jwt import token_service
from src.infrastructure.services.encryption import credentials_protector
from src.infrastructure.services.hashing import password_hasher, token_hasher
from src.infrastructure.services.email import EmailService

from fastapi import BackgroundTasks


def get_video_processor() -> IVideoProcessor:
    return video_processor


def get_token_service() -> ITokenService:
    return token_service


def get_credentials_protector() -> ICredentialsProtector:
    return credentials_protector


def get_password_hasher() -> IPasswordHasher:
    return password_hasher


def get_token_hasher() -> ITokenHasher:
    return token_hasher


def get_email_service(background_tasks: BackgroundTasks) -> IEmailService:
    return EmailService(background_tasks=background_tasks)
