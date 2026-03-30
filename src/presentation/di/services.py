from fastapi import BackgroundTasks

from src.domain.interfaces.services import (
    ICredentialsProtector,
    IEmailService,
    IPasswordHasher,
    ITokenHasher,
    ITokenService,
    IVideoProcessor,
)
from src.infrastructure.services.email import EmailService
from src.infrastructure.services.encryption import (
    get_credentials_protector as _get_credentials_protector,
)
from src.infrastructure.services.hashing import password_hasher, token_hasher
from src.infrastructure.services.jwt import (
    get_token_service as _get_token_service,
)
from src.infrastructure.services.video_processing import (
    get_video_processor as _get_video_processor,
)


def get_video_processor() -> IVideoProcessor:
    return _get_video_processor()


def get_token_service() -> ITokenService:
    return _get_token_service()


def get_credentials_protector() -> ICredentialsProtector:
    return _get_credentials_protector()


def get_password_hasher() -> IPasswordHasher:
    return password_hasher


def get_token_hasher() -> ITokenHasher:
    return token_hasher


def get_email_service(background_tasks: BackgroundTasks) -> IEmailService:
    return EmailService(background_tasks=background_tasks)
