from datetime import datetime
from pydantic import BaseModel
from src.domain.enums import SocialPlatform


class ConnectSocialAccountDTO(BaseModel):
    """Generic DTO for connecting any social media account."""

    user_id: str
    platform_account_id: str
    platform: SocialPlatform
    credentials: dict


class DisconnectSocialAccountDTO(BaseModel):
    """Generic DTO for disconnecting any social media account."""

    user_id: str
    platform_account_id: str
    platform: SocialPlatform


class CheckSocialAccountStatusDTO(BaseModel):
    """Generic DTO for checking the status of any social media account."""

    user_id: str
    platform_account_id: str
    platform: SocialPlatform


class SocialAccountStatusDTO(BaseModel):
    """DTO representing the status of a social account."""

    is_connected: bool
    expiry_date: datetime | None


class ConnectSocialAccountResponseDTO(BaseModel):
    """Response DTO for social account connection."""

    message: str
    platform: SocialPlatform
    connected_at: datetime


class ListSocialAccountsDTO(BaseModel):
    """Request DTO for listing user's social accounts."""

    user_id: str


class SocialAccountSummaryDTO(BaseModel):
    """Summary information for a social account (no credentials)."""

    id: str
    platform: str
    platform_account_id: str
    connected_at: datetime


class ListSocialAccountsResponseDTO(BaseModel):
    """Response DTO for listing social accounts."""

    accounts: list[SocialAccountSummaryDTO]
    total_count: int
