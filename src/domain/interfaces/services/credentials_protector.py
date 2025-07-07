from src.domain.dtos.encryption.encryption import (
    ProtectCredentialsDTO, ProtectedCredentialsDTO,
    UnprotectCredentialsDTO, UnprotectedCredentialsDTO
)

from abc import ABC, abstractmethod


class ICredentialsProtector(ABC):
    """
    Domain service for protecting sensitive credentials before storage.
    
    This service handles the protection/unprotection of credentials but does NOT
    handle their storage or retrieval - that's the repository's responsibility.
    Typically used for protecting OAuth tokens, API keys, and other sensitive
    account credentials.
    """
    
    @abstractmethod
    def protect(self, dto: ProtectCredentialsDTO) -> ProtectedCredentialsDTO:
        """Protect sensitive credentials before storing them."""
        pass

    @abstractmethod
    def unprotect(self, dto: UnprotectCredentialsDTO) -> UnprotectedCredentialsDTO:
        """Unprotect credentials after retrieving them from storage."""
        pass
