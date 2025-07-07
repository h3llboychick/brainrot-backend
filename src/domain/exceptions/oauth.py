from src.domain.exceptions.base import BaseAppException


class OAuthError(BaseAppException):
    """Base exception for OAuth-related errors."""
    status_code = 400
    
    def __init__(self, message: str = "OAuth authentication failed"):
        super().__init__(message)


class InvalidOAuthStateError(OAuthError):
    """Exception raised when OAuth state validation fails."""
    
    def __init__(self, message: str = "Invalid OAuth state. Possible CSRF attack or expired session"):
        super().__init__(message)


class OAuthCredentialsError(OAuthError):
    """Exception raised when obtaining OAuth credentials fails."""
    
    def __init__(self, platform: str, details: str = None):
        msg = f"Failed to obtain {platform} credentials"
        if details:
            msg += f": {details}"
        super().__init__(msg)
        self.platform = platform


class OAuthTokenExchangeError(OAuthError):
    """Exception raised when exchanging OAuth authorization code for tokens fails."""
    
    def __init__(self, platform: str, details: str = None):
        msg = f"Failed to exchange authorization code for {platform} tokens"
        if details:
            msg += f": {details}"
        super().__init__(msg)
        self.platform = platform


class OAuthAuthorizationError(OAuthError):
    """Exception raised when OAuth authorization fails."""
    
    def __init__(self, platform: str, details: str = None):
        msg = f"Failed to authorize with {platform}"
        if details:
            msg += f": {details}"
        super().__init__(msg)
        self.platform = platform
