from src.domain.interfaces.services.video_processor import IVideoProcessor
from src.domain.interfaces.services.token_service import ITokenService
from src.domain.interfaces.services.credentials_protector import ICredentialsProtector
from src.domain.interfaces.services.password_hasher import IPasswordHasher
from src.domain.interfaces.services.email_service import IEmailService
from src.domain.interfaces.services.token_hasher import ITokenHasher


from src.infrastructure.services.video_processing.celery_video_processor import video_processor
from src.infrastructure.services.jwt.token_service import token_service 
from src.infrastructure.services.encryption.envelope_encryptor import credentials_protector
from src.infrastructure.services.hashing.password_hasher import password_hasher
from src.infrastructure.services.hashing.token_hasher import token_hasher
from src.infrastructure.services.email.email_service import EmailService

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
    return EmailService(
        background_tasks=background_tasks
    )