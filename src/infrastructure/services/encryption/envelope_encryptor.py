from src.domain.dtos.encryption import (
    ProtectCredentialsDTO,
    ProtectedCredentialsDTO,
    UnprotectCredentialsDTO,
    UnprotectedCredentialsDTO,
)
from src.domain.interfaces.services import ICredentialsProtector

from src.infrastructure.services.encryption.settings import settings
from src.infrastructure.logging import get_logger

from cryptography.hazmat.primitives.keywrap import aes_key_wrap, aes_key_unwrap
from cryptography.fernet import Fernet
import secrets
import base64

logger = get_logger("app")


class EnvelopeEncryptor(ICredentialsProtector):
    """
    Infrastructure implementation of credentials protection using envelope encryption.

    Uses a two-tier key system:
    - KEK (Key Encryption Key): Master key for wrapping data keys
    - DEK (Data Encryption Key): Generated per-encryption for actual data

    This approach provides key rotation capabilities and enhanced security.
    """

    def __init__(self, kek: str):
        self.kek = bytes.fromhex(kek)

    def protect(self, dto: ProtectCredentialsDTO) -> ProtectedCredentialsDTO:
        """Protect credentials using envelope encryption."""
        dek = secrets.token_bytes(32)
        fernet = Fernet(base64.urlsafe_b64encode(dek))
        ciphertext = fernet.encrypt(dto.plaintext)

        wrapped_key = aes_key_wrap(self.kek, dek)

        return ProtectedCredentialsDTO(ciphertext=ciphertext, wrapped_key=wrapped_key)

    def unprotect(self, dto: UnprotectCredentialsDTO) -> UnprotectedCredentialsDTO:
        """Unprotect credentials by decrypting with the wrapped key."""
        dek = aes_key_unwrap(self.kek, dto.wrapped_key)
        fernet = Fernet(base64.urlsafe_b64encode(dek))
        plaintext = fernet.decrypt(dto.ciphertext)

        return UnprotectedCredentialsDTO(plaintext=plaintext)


credentials_protector = EnvelopeEncryptor(kek=settings.KEK_KEY)
