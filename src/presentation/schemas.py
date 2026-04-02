from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from src.domain.enums import SocialPlatform


class UserEmailRegistrationRequest(BaseModel):
    email: EmailStr = Field(EmailStr, example="user@example.com")
    password: str = Field(str, min_length=8, example="strongpassword123")


class UserEmailRegistrationResponse(BaseModel):
    message: str = Field(
        str, example="User registered successfully. Please verify your email."
    )


class UserEmailLoginRequest(BaseModel):
    email: EmailStr = Field(EmailStr, example="user@example.com")
    password: str = Field(str, min_length=8, example="strongpassword123")


class AuthenticationResponse(BaseModel):
    access_token: str = Field(str, example="example_access_token")
    access_token_expires_at: datetime = Field(
        datetime, example="2024-12-31T23:59:59Z"
    )
    refresh_token: str = Field(str, example="example_refresh_token")
    refresh_token_expires_at: datetime = Field(
        datetime, example="2025-12-31T23:59:59Z"
    )


class UserEmailVerificationCodeRequest(BaseModel):
    email: EmailStr = Field(example="user@example.com")
    verification_code: str = Field(example="123456")


class RefreshAccessTokenResponse(BaseModel):
    access_token: str = Field(example="example_access_token")
    access_token_expires_at: datetime = Field(example="2024-12-31T23:59:59Z")


class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    is_verified: bool
    created_at: datetime


class VideoGenerationRequest(BaseModel):
    format_id: int = Field(example=1)
    prompt: str = Field(example="Create a funny video about cats.")
    platform: SocialPlatform | None = Field(
        default=None,
        example=SocialPlatform.youtube,
        description="Optional platform to publish the video after generation.",
    )


class VideoGenerationResponse(BaseModel):
    video_job_id: str = Field(example="vj_123")


class VideoFormatResponse(BaseModel):
    id: int = Field(example=1)
    name: str = Field(example="would_you_rather")
    description: str | None = Field(
        default=None, example="A fun Would You Rather format"
    )
    price: float = Field(example=1.5)


class ListVideoFormatsResponse(BaseModel):
    formats: list[VideoFormatResponse] = Field(default_factory=list)
    total_count: int = Field(example=3)


class SocialAccountConnectResponse(BaseModel):
    message: str = Field(example="YouTube account connected successfully.")
    platform: SocialPlatform = Field(example=SocialPlatform.youtube)
    connected_at: datetime = Field(example="2024-12-31T23:59:59Z")


class SocialAccountDisconnectResponse(BaseModel):
    message: str = Field(example="YouTube account disconnected successfully.")
    platform: SocialPlatform = Field(example=SocialPlatform.youtube)


class SocialAccountStatusResponse(BaseModel):
    """Response for checking account status."""

    message: str = Field(example="YouTube account is connected and valid.")
    platform: str = Field(example="youtube")
    is_valid: bool = Field(example=True)


class SocialAccountSummary(BaseModel):
    """Summary of a connected social account."""

    id: str = Field(example="sa_123")
    platform: str = Field(example="youtube")
    platform_account_id: str = Field(example="UC_x5XG1OV2P6uZZ5FSM9Ttw")
    connected_at: datetime = Field(example="2024-12-31T23:59:59Z")


class ListSocialAccountsResponse(BaseModel):
    """Response for listing all user's connected accounts."""

    accounts: list[SocialAccountSummary] = Field(example=[])
    total_count: int = Field(example=0)


class UserMeInformationResponse(BaseModel):
    user_id: str = Field(example="user_123")


class UserBalanceResponse(BaseModel):
    balance: float = Field(example=100.0, description="Total balance")
    reserved_balance: float = Field(
        example=20.0, description="Funds reserved for pending jobs"
    )
    available_balance: float = Field(
        example=80.0, description="Balance available for new jobs"
    )


class CheckoutRequest(BaseModel):
    price_id: str | None = Field(
        default=None,
        example="price_abc123",
        description="Pre-defined token package price ID (mutually exclusive with token_count)",
    )
    token_count: int | None = Field(
        default=None,
        example=250,
        description="Custom token amount to purchase (mutually exclusive with price_id)",
    )


class CheckoutResponse(BaseModel):
    checkout_url: str = Field(
        example="https://checkout.stripe.com/c/pay/cs_test_...",
        description="Stripe Checkout URL to redirect the user to",
    )
