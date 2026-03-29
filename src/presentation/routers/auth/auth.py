from typing import Annotated

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse

from src.domain.dtos.auth import (
    EmailLoginDTO,
    EmailRegistrationDTO,
    EmailVerificationDTO,
    GoogleSignInDTO,
    RefreshAccessTokenDTO,
)
from src.domain.exceptions import OAuthAuthorizationError
from src.domain.use_cases.auth import (
    LoginUserEmailUseCase,
    RefreshAccessTokenUseCase,
    RegisterUserEmailUseCase,
    SignInWithGoogleUseCase,
    VerifyUserEmailUseCase,
)
from src.infrastructure.rate_limiting import limiter
from src.presentation.di.auth import (
    get_confirm_user_email_use_case,
    get_login_user_email_use_case,
    get_refresh_access_token_use_case,
    get_register_user_email_use_case,
    get_signin_with_google_use_case,
    token_scheme,
)
from src.presentation.routers.auth.settings import google_auth_settings
from src.presentation.schemas import (
    AuthenticationResponse,
    RefreshAccessTokenResponse,
    UserEmailLoginRequest,
    UserEmailRegistrationRequest,
    UserEmailRegistrationResponse,
    UserEmailVerificationCodeRequest,
)

oauth = OAuth()

oauth.register(
    name="google",
    client_id=google_auth_settings.GOOGLE_CLIENT_ID,
    client_secret=google_auth_settings.GOOGLE_CLIENT_SECRET,
    authorize_url="https://accounts.google.com/o/oauth2/auth",  # nosec: B106
    authorize_params=None,
    access_token_url="https://accounts.google.com/o/oauth2/token",
    access_token_params=None,
    refresh_token_url=None,
    authorize_state=google_auth_settings.SECRET_KEY,
    redirect_uri=google_auth_settings.GOOGLE_REDIRECT_URL,
    jwks_uri="https://www.googleapis.com/oauth2/v3/certs",
    client_kwargs={"scope": "openid email profile"},
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserEmailRegistrationResponse,
    status_code=201,
    description="Register a new user with email and password. A verification code will be sent to the email.",
)
@limiter.limit("3/minute")
async def register_router(
    request: Request,
    registration_data: UserEmailRegistrationRequest,
    use_case: Annotated[
        RegisterUserEmailUseCase, Depends(get_register_user_email_use_case)
    ],
):
    await use_case.execute(
        EmailRegistrationDTO(
            email=registration_data.email, password=registration_data.password
        )
    )
    return UserEmailRegistrationResponse(
        message="Registration successful, please check your email for the verification code.",
        email=registration_data.email,
    )


@router.post(
    "/verify-email",
    response_model=UserEmailRegistrationResponse,
    description="Verify user's email using the verification code sent to their email.",
    status_code=200,
)
@limiter.limit("3/minute")
async def verify_email_router(
    request: Request,
    code_data: UserEmailVerificationCodeRequest,
    use_case: Annotated[
        VerifyUserEmailUseCase, Depends(get_confirm_user_email_use_case)
    ],
):
    await use_case.execute(
        EmailVerificationDTO(
            email=code_data.email, verification_code=code_data.verification_code
        )
    )
    return UserEmailRegistrationResponse(message="Email verified successfully.")


@router.get(
    "/login/google",
    status_code=302,
    description="Initiate Google OAuth login flow. Redirects user to Google's OAuth consent screen.",
)
@limiter.limit("3/minute")
async def google_login(request: Request):
    """
    Initiate Google OAuth login flow.
    Redirects user to Google's OAuth consent screen.
    """
    frontend_url = google_auth_settings.GOOGLE_FRONTEND_URL
    redirect_url = google_auth_settings.GOOGLE_REDIRECT_URL
    request.session["login_redirect"] = frontend_url

    return await oauth.google.authorize_redirect(
        request, redirect_url, prompt="consent"
    )


@router.get(
    "/google/callback",
    status_code=302,
    description="Handle Google OAuth callback and authenticate user.",
)
@limiter.limit("3/minute")
async def google_callback(
    request: Request,
    use_case: Annotated[
        SignInWithGoogleUseCase, Depends(get_signin_with_google_use_case)
    ],
):
    """
    Handle Google OAuth callback after user grants permissions.
    Authenticates user and returns tokens via cookies and redirect.
    """
    # Edge case: Convert third-party OAuth library exceptions to domain exceptions
    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise OAuthAuthorizationError(platform="Google", details=str(e)) from e

    email = token.get("userinfo").get("email")
    google_id = token.get("userinfo").get("sub")

    result = await use_case.execute(GoogleSignInDTO(email=email, google_id=google_id))

    redirect_url = request.session.get("login_redirect")
    response = RedirectResponse(url=redirect_url)

    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token.token,
        httponly=True,
        max_age=result.refresh_token.expires_at,
        samesite="lax",
        secure=True,
    )

    # INSECURE COOKIE, FOR DEMO PURPOSES ONLY
    response.set_cookie(
        key="Authorization",
        value=f"Bearer {result.access_token.token}",
        httponly=False,
        max_age=result.access_token.expires_at,
        samesite="lax",
        secure=True,
    )

    return response


@router.post(
    "/login",
    response_model=AuthenticationResponse,
    description="Log in a user with email and password. Returns access and refresh tokens.",
    status_code=200,
)
@limiter.limit("5/minute")
async def login_router(
    request: Request,
    response: Response,
    registration_data: UserEmailLoginRequest,
    use_case: Annotated[LoginUserEmailUseCase, Depends(get_login_user_email_use_case)],
):
    result = await use_case.execute(
        EmailLoginDTO(
            email=registration_data.email, password=registration_data.password
        )
    )

    response.set_cookie(
        key="refresh_token",
        value=result.refresh_token.token,
        httponly=True,
        max_age=result.refresh_token.expires_at,
        samesite="lax",
        secure=True,
    )

    return AuthenticationResponse(
        access_token=result.access_token.token,
        access_token_expires_at=result.access_token.expires_at,
        refresh_token=result.refresh_token.token,
        refresh_token_expires_at=result.refresh_token.expires_at,
    )


@router.post(
    "/refresh-token",
    response_model=RefreshAccessTokenResponse,
    description="Refresh access token using a valid refresh token. Returns new access token.",
    status_code=200,
)
@limiter.limit("3/minute")
async def refresh_token_router(
    request: Request,
    token: Annotated[str, Depends(token_scheme)],
    use_case: Annotated[
        RefreshAccessTokenUseCase, Depends(get_refresh_access_token_use_case)
    ],
):
    result = await use_case.execute(RefreshAccessTokenDTO(refresh_token=token))

    return RefreshAccessTokenResponse(
        access_token=result.token,
        access_token_expires_at=result.expires_at,
    )
