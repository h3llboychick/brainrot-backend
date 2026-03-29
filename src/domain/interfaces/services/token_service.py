from abc import ABC, abstractmethod

from src.domain.dtos.auth import CreateTokenPayloadDTO, TokenDTO


class ITokenService(ABC):
    @abstractmethod
    def create_token_pair(
        self, payload: CreateTokenPayloadDTO
    ) -> tuple[TokenDTO, TokenDTO]:
        """
        Create an access token and a refresh token with the given data and expiration time.
        """
        pass

    @abstractmethod
    def decode_token(self, token: str) -> TokenDTO:
        """
        Decode token and return the payload.
        """
        pass

    @abstractmethod
    def validate_access_token(self, token: str) -> TokenDTO:
        """
        Decode and validate that the token is an access token.
        Raises InvalidTokenTypeError if the token is not an access token.
        """
        pass

    @abstractmethod
    def validate_refresh_token(self, token: str) -> TokenDTO:
        """
        Decode and validate that the token is a refresh token.
        Raises InvalidTokenTypeError if the token is not a refresh token.
        """
        pass

    @abstractmethod
    def renew_access_token(self, payload: CreateTokenPayloadDTO) -> TokenDTO:
        """
        Issue a new access token from an already-validated payload.
        """
        pass
