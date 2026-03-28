from src.domain.dtos.auth import TokenDTO, TokenPayloadDTO, CreateTokenPayloadDTO

from abc import ABC, abstractmethod


class ITokenService(ABC):
    @abstractmethod
    def create_token_pair(self, payload: CreateTokenPayloadDTO) -> list[TokenDTO]:
        """
        Create an access token with the given data and expiration time.
        """
        pass

    @abstractmethod
    def decode_token(self, token: str) -> TokenPayloadDTO:
        """
        Decode token and return the payload.
        """
        pass

    @abstractmethod
    def renew_access_token(self, refresh_token: str) -> TokenDTO:
        """
        Issue a new access token using the provided refresh token.
        """
        pass
