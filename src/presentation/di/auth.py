from src.domain.use_cases.auth.register_user_email import RegisterUserEmailUseCase
from src.domain.use_cases.auth.verify_user_email import VerifyUserEmailUseCase
from src.domain.use_cases.auth.login_user_email import LoginUserEmailUseCase
from src.domain.use_cases.auth.refresh_access_token import RefreshAccessTokenUseCase
from src.domain.use_cases.auth.sign_in_with_google import SignInWithGoogleUseCase

from src.domain.interfaces.services import IEmailService, IPasswordHasher, ITokenService
from src.domain.interfaces.repositories import (
    IVerificationCodeRepository,
    IUserRepository,
    ITokenRepository,
)

from src.domain.exceptions import InvalidTokenTypeError
from src.domain.dtos.auth import TokenDTO
from src.domain.enums import TokenType

from src.presentation.di.repositories import (
    get_user_repository,
    get_token_repository,
    get_verification_code_repository,
)
from src.presentation.di.services import (
    get_email_service,
    get_token_service,
    get_password_hasher,
)


from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from starlette.status import HTTP_403_FORBIDDEN

from typing import Annotated, Optional


class TokenBearer(OAuth2):
    def __init__(
        self,
        tokenUrl: str,
        scheme_name: str | None = None,
        scopes: dict | None = None,
        auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        header_authorization: str = request.headers.get("Authorization")
        cookie_authorization: str = request.cookies.get("Authorization")

        cookies_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization
        )

        if cookie_authorization and cookies_scheme.lower() == "bearer":
            return cookie_param
        scheme, param = get_authorization_scheme_param(header_authorization)

        if not header_authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None

        return param


token_scheme = TokenBearer(tokenUrl="/auth/login")


async def get_token_payload(
    token: Annotated[str, Depends(token_scheme)],
    token_service: Annotated[ITokenService, Depends(get_token_service)],
) -> TokenDTO:
    return token_service.validate_access_token(token)


def get_register_user_email_use_case(
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
    email_service: Annotated[IEmailService, Depends(get_email_service)],
    verification_code_repository: Annotated[
        IVerificationCodeRepository, Depends(get_verification_code_repository)
    ],
    password_hasher: Annotated[IPasswordHasher, Depends(get_password_hasher)],
) -> RegisterUserEmailUseCase:
    return RegisterUserEmailUseCase(
        user_repository=user_repository,
        email_service=email_service,
        verification_code_repository=verification_code_repository,
        password_hasher=password_hasher,
    )


def get_confirm_user_email_use_case(
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
    verification_code_repository: Annotated[
        IVerificationCodeRepository, Depends(get_verification_code_repository)
    ],
    email_service: Annotated[IEmailService, Depends(get_email_service)],
) -> VerifyUserEmailUseCase:
    return VerifyUserEmailUseCase(
        user_repository=user_repository,
        verification_code_repository=verification_code_repository,
        email_service=email_service,
    )


def get_login_user_email_use_case(
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
    token_service: Annotated[ITokenService, Depends(get_token_service)],
    token_repository: Annotated[ITokenRepository, Depends(get_token_repository)],
    password_hasher: Annotated[IPasswordHasher, Depends(get_password_hasher)],
) -> LoginUserEmailUseCase:
    return LoginUserEmailUseCase(
        user_repository=user_repository,
        token_service=token_service,
        token_repository=token_repository,
        password_hasher=password_hasher,
    )


def get_signin_with_google_use_case(
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
    token_service: Annotated[ITokenService, Depends(get_token_service)],
    token_repository: Annotated[ITokenRepository, Depends(get_token_repository)],
) -> SignInWithGoogleUseCase:
    return SignInWithGoogleUseCase(
        user_repository=user_repository,
        token_service=token_service,
        token_repository=token_repository,
    )


def get_refresh_access_token_use_case(
    token_repository: Annotated[ITokenRepository, Depends(get_token_repository)],
    token_service: Annotated[ITokenService, Depends(get_token_service)],
) -> RefreshAccessTokenUseCase:
    return RefreshAccessTokenUseCase(
        token_repository=token_repository, token_service=token_service
    )


async def get_current_user_id(
    token: Annotated[TokenDTO, Depends(get_token_payload)],
) -> str:
    if token.type != TokenType.ACCESS:
        raise InvalidTokenTypeError()
    user_id = token.payload.user_id
    return user_id
