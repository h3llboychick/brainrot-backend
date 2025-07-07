from pydantic import BaseModel
from datetime import datetime


class UserEmailRegistrationRequest(BaseModel):
    email: str
    password: str

class UserEmailRegistrationResponse(BaseModel):
    message: str

class UserEmailLoginRequest(BaseModel):
    email: str
    password: str

class AuthenticationResponse(BaseModel):
    access_token: str 
    access_token_expires_at: datetime 
    refresh_token: str 
    refresh_token_expires_at: datetime 

class UserEmailVerificationCodeRequest(BaseModel):
    email: str
    verification_code: str

class RefreshAccessTokenResponse(BaseModel):
    access_token: str 
    access_token_expires_at: datetime 

class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    is_verified: bool
    created_at: datetime

class VideoGenerationRequest(BaseModel):
    format_id: int
    prompt: str
    platform: str

class VideoGenerationResponse(BaseModel):
    video_job_id: str

class SocialAccountConnectResponse(BaseModel):
    message: str
    platform: str
    connected_at: datetime

class SocialAccountDisconnectResponse(BaseModel):
    message: str
    platform: str

class SocialAccountStatusResponse(BaseModel):
    """Response for checking account status."""
    message: str
    platform: str
    is_valid: bool = True

class SocialAccountSummary(BaseModel):
    """Summary of a connected social account."""
    id: str
    platform: str
    platform_account_id: str
    connected_at: datetime

class ListSocialAccountsResponse(BaseModel):
    """Response for listing all user's connected accounts."""
    accounts: list[SocialAccountSummary]
    total_count: int

class UserMeInformationResponse(BaseModel):
    user_id: str