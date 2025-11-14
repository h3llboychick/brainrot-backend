from src.domain.use_cases.social_accounts.connect_social_account import ConnectSocialAccountUseCase
from src.domain.use_cases.social_accounts.check_social_account_status import CheckSocialAccountStatusUseCase
from src.domain.use_cases.social_accounts.disconnect_social_account import DisconnectSocialAccountUseCase
from src.domain.use_cases.social_accounts.list_social_accounts import ListSocialAccountsUseCase
from src.domain.dtos.social_accounts.base import ConnectSocialAccountDTO, DisconnectSocialAccountDTO, CheckSocialAccountStatusDTO, ListSocialAccountsDTO
from src.domain.enums.social_platform import SocialPlatform
from src.domain.exceptions.oauth import InvalidOAuthStateError, OAuthTokenExchangeError
from src.domain.exceptions.social_accounts import (
    UnsupportedSocialPlatformError, 
    ValidatorNotFoundError,
    NoYouTubeChannelFoundError
)

from src.infrastructure.redis.repositories.youtube_oauth_state.youtube_oauth_state_repository import YouTubeOAuthStateRepository
from src.infrastructure.services.validators.validator_registry import ValidatorRegistry

from src.presentation.di.auth import get_current_user_id
from src.presentation.di.social_accounts import (
    get_connect_social_account_use_case, 
    get_disconnect_social_account_use_case,
    get_check_account_status_use_case,
    get_list_social_accounts_use_case
)
from src.presentation.di.repositories import get_youtube_oauth_state_repository
from src.presentation.routers.accounts.settings import youtube_auth_settings
from src.presentation.schemas import (
    SocialAccountConnectResponse, 
    SocialAccountDisconnectResponse,
    SocialAccountStatusResponse,
    ListSocialAccountsResponse,
    SocialAccountSummary
)

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

from typing import Annotated
from datetime import datetime


# set OAUTHLIB_INSECURE_TRANSPORT=1
router = APIRouter(prefix="/accounts", tags=["social accounts"])

@router.get("/youtube/connect")
async def link_youtube_account(
    user_id: Annotated[str, Depends(get_current_user_id)],
    state_storage: Annotated[YouTubeOAuthStateRepository, Depends(get_youtube_oauth_state_repository)]
) -> RedirectResponse:
    """
    Initiate YouTube account connection via OAuth2.
    Redirects user to Google's OAuth consent screen.
    """
    flow = Flow.from_client_secrets_file(
        youtube_auth_settings.YOUTUBE_CLIENT_SECRET_FILE_PATH,
        scopes=youtube_auth_settings.YOUTUBE_SCOPES_LIST,
        redirect_uri=youtube_auth_settings.YOUTUBE_REDIRECT_URI
    )

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="false",
        prompt="consent"
    )
    await state_storage.save_state(user_id, state)

    return RedirectResponse(auth_url, status_code=status.HTTP_302_FOUND)

@router.get("/youtube/callback")
async def youtube_callback(
    request: Request,
    state: str,
    user_id: Annotated[str, Depends(get_current_user_id)],
    use_case: Annotated[ConnectSocialAccountUseCase, Depends(get_connect_social_account_use_case)],
    state_storage: Annotated[YouTubeOAuthStateRepository, Depends(get_youtube_oauth_state_repository)]
) -> SocialAccountConnectResponse:
    """
    Handle YouTube OAuth2 callback after user grants permissions.
    Validates state and stores YouTube credentials.
    """
    # Validate OAuth state to prevent CSRF attacks
    stored_state = await state_storage.get_state(user_id)
    if not state or state != stored_state:
        raise InvalidOAuthStateError()
    
    # Edge case: Convert third-party OAuth library exceptions to domain exceptions
    try:
        flow = Flow.from_client_secrets_file(
            youtube_auth_settings.YOUTUBE_CLIENT_SECRET_FILE_PATH,
            scopes=youtube_auth_settings.YOUTUBE_SCOPES_LIST,
            redirect_uri=youtube_auth_settings.YOUTUBE_REDIRECT_URI
        )
        flow.fetch_token(authorization_response=str(request.url))
        credentials = flow.credentials
    except Exception as e:
        raise OAuthTokenExchangeError(platform="YouTube", details=str(e)) from e
    
    youtube = build("youtube", "v3", credentials=credentials)

    resp = youtube.channels().list(part="id,snippet", mine=True).execute()
    items = resp.get("items", [])
    if not items:
        raise NoYouTubeChannelFoundError()
    # think about asking user to select channel if multiple exist
    primary_channel_id = items[0]["id"]


    result = await use_case.execute(
        ConnectSocialAccountDTO(
            user_id=user_id,
            platform_account_id=primary_channel_id,
            platform=SocialPlatform.youtube,
            credentials={
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "scopes": credentials.scopes,
            }
        )
    )

    return SocialAccountConnectResponse(
        message=result.message,
        platform=SocialPlatform.youtube.value,
        connected_at=datetime.utcnow()
    )

@router.get("/{platform}/status")
async def check_account_status(
    platform: str,
    platform_account_id: str,
    user_id: Annotated[str, Depends(get_current_user_id)],
    use_case: Annotated[CheckSocialAccountStatusUseCase, Depends(get_check_account_status_use_case)]
) -> SocialAccountStatusResponse:
    """
    Check the status of a connected social account.
    
    Generic endpoint that works for any platform (YouTube, TikTok, Instagram, etc.).
    Validates credentials and returns connection status.
    
    Path parameters:
        platform: Platform name (youtube, tiktok, instagram)
        
    Query parameters:
        platform_account_id: The platform-specific account identifier
        
    Returns:
        SocialAccountStatusResponse with validation status
        
    Raises:
        UnsupportedSocialPlatformError: If platform is not supported
        ValidatorNotFoundError: If no validator exists for the platform
    """
    # Validate platform enum
    try:
        platform_enum = SocialPlatform(platform)
    except ValueError:
        valid_platforms = [p.value for p in SocialPlatform]
        raise UnsupportedSocialPlatformError(platform=platform, valid_platforms=valid_platforms)
    
    # Get platform-specific validator
    try:
        validator = ValidatorRegistry.get_validator(platform)
    except ValueError:
        raise ValidatorNotFoundError(platform=platform)
    
    # Inject validator into use case
    use_case.validator = validator
    
    await use_case.execute(
        CheckSocialAccountStatusDTO(
            user_id=user_id, 
            platform=platform_enum,
            platform_account_id=platform_account_id
        )
    )

    return SocialAccountStatusResponse(
        message=f"{platform.capitalize()} account is connected and valid.",
        platform=platform,
        is_valid=True
    )

@router.delete("/{platform}")
async def disconnect_account(
    platform: str,
    platform_account_id: str,
    user_id: Annotated[str, Depends(get_current_user_id)],
    use_case: Annotated[DisconnectSocialAccountUseCase, Depends(get_disconnect_social_account_use_case)]
) -> SocialAccountDisconnectResponse:
    """
    Disconnect a social account.
    
    Generic endpoint that works for any platform (YouTube, TikTok, Instagram, etc.).
    Removes stored credentials for the specified account.
    
    Path parameters:
        platform: Platform name (youtube, tiktok, instagram)
        
    Query parameters:
        platform_account_id: The platform-specific account identifier
        
    Returns:
        SocialAccountDisconnectResponse confirming disconnection
        
    Raises:
        UnsupportedSocialPlatformError: If platform is not supported
    """
    # Validate platform enum
    try:
        platform_enum = SocialPlatform(platform)
    except ValueError:
        valid_platforms = [p.value for p in SocialPlatform]
        raise UnsupportedSocialPlatformError(platform=platform, valid_platforms=valid_platforms)
    
    await use_case.execute(
        DisconnectSocialAccountDTO(
            user_id=user_id,
            platform=platform_enum,
            platform_account_id=platform_account_id
        )
    )

    return SocialAccountDisconnectResponse(
        message=f"{platform.capitalize()} account disconnected successfully",
        platform=platform
    )


@router.get("/list")
async def list_connected_accounts(
    user_id: Annotated[str, Depends(get_current_user_id)],
    use_case: Annotated[ListSocialAccountsUseCase, Depends(get_list_social_accounts_use_case)]
) -> ListSocialAccountsResponse:
    result = await use_case.execute(
        ListSocialAccountsDTO(user_id=user_id)
    )
    
    return ListSocialAccountsResponse(
        accounts=[
            SocialAccountSummary(
                id=account.id,
                platform=account.platform,
                platform_account_id=account.platform_account_id,
                connected_at=account.connected_at
            )
            for account in result.accounts
        ],
        total_count=result.total_count
    )

