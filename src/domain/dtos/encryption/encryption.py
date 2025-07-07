from pydantic import BaseModel


class ProtectCredentialsDTO(BaseModel):
    """Sensitive credentials that need protection before storage."""
    plaintext: bytes


class ProtectedCredentialsDTO(BaseModel):
    """Credentials secured and ready for storage."""
    ciphertext: bytes
    wrapped_key: bytes


class UnprotectCredentialsDTO(BaseModel):
    """Protected credentials retrieved from storage that need to be revealed."""
    ciphertext: bytes
    wrapped_key: bytes


class UnprotectedCredentialsDTO(BaseModel):
    """Revealed credentials ready for use."""
    plaintext: bytes