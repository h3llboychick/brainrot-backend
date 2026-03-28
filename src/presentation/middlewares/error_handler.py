from src.domain.exceptions import (
    InvalidTokenError,
    ExpiredTokenError,
    InvalidTokenPayloadError,
    InvalidTokenTypeError,
    UserNotActiveError,
    UserNotVerifiedError,
    InvalidCredentialsError,
    VerificationCodeNotFoundError,
    InvalidVerificationCodeError,
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidOAuthStateError,
    OAuthCredentialsError,
    OAuthTokenExchangeError,
    OAuthAuthorizationError,
    OAuthError,
    ExpiredSocialAccountCredentialsError,
    InvalidSocialAccountCredentialsError,
    NotFoundSocialAccountError,
)

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(InvalidTokenError)
    async def invalid_token_exception_handler(request, exc: InvalidTokenError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content={"message": str(exc)}
        )

    @app.exception_handler(ExpiredTokenError)
    async def expired_token_exception_handler(request, exc: ExpiredTokenError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content={"message": str(exc)}
        )

    @app.exception_handler(InvalidTokenPayloadError)
    async def invalid_token_payload_exception_handler(
        request, exc: InvalidTokenPayloadError
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content={"message": str(exc)}
        )

    @app.exception_handler(InvalidTokenTypeError)
    async def invalid_token_type_exception_handler(request, exc: InvalidTokenTypeError):
        return JSONResponse(status_code=401, content={"message": str(exc)})

    @app.exception_handler(UserNotActiveError)
    async def user_not_active_exception_handler(request, exc: UserNotActiveError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"message": str(exc)}
        )

    @app.exception_handler(UserNotVerifiedError)
    async def user_not_verified_exception_handler(request, exc: UserNotVerifiedError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={"message": str(exc)}
        )

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials_exception_handler(
        request, exc: InvalidCredentialsError
    ):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED, content={"message": str(exc)}
        )

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_exception_handler(request, exc: UserNotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": str(exc)}
        )

    @app.exception_handler(UserAlreadyExistsError)
    async def user_already_exists_exception_handler(
        request, exc: UserAlreadyExistsError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT, content={"message": str(exc)}
        )

    @app.exception_handler(VerificationCodeNotFoundError)
    async def verification_code_not_found_exception_handler(
        request, exc: VerificationCodeNotFoundError
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": str(exc)}
        )

    @app.exception_handler(InvalidVerificationCodeError)
    async def invalid_verification_code_exception_handler(
        request, exc: InvalidVerificationCodeError
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(exc)}
        )

    @app.exception_handler(InvalidOAuthStateError)
    async def invalid_oauth_state_handler(request, exc: InvalidOAuthStateError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(exc)}
        )

    @app.exception_handler(OAuthCredentialsError)
    async def oauth_credentials_error_handler(request, exc: OAuthCredentialsError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(exc), "platform": exc.platform},
        )

    @app.exception_handler(OAuthTokenExchangeError)
    async def oauth_token_exchange_error_handler(request, exc: OAuthTokenExchangeError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(exc), "platform": exc.platform},
        )

    @app.exception_handler(OAuthAuthorizationError)
    async def oauth_authorization_error_handler(request, exc: OAuthAuthorizationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": str(exc), "platform": exc.platform},
        )

    @app.exception_handler(OAuthError)
    async def oauth_error_handler(request, exc: OAuthError):
        return JSONResponse(status_code=exc.status_code, content={"message": str(exc)})

    @app.exception_handler(ExpiredSocialAccountCredentialsError)
    async def expired_social_account_credentials_handler(
        request, exc: ExpiredSocialAccountCredentialsError
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(exc)}
        )

    @app.exception_handler(InvalidSocialAccountCredentialsError)
    async def invalid_social_account_credentials_handler(
        request, exc: InvalidSocialAccountCredentialsError
    ):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={"message": str(exc)}
        )

    @app.exception_handler(NotFoundSocialAccountError)
    async def not_found_social_account_handler(
        request, exc: NotFoundSocialAccountError
    ):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={"message": str(exc)}
        )
