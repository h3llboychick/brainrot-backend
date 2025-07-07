from src.domain.exceptions.base import BaseAppException


class AuthenticationError(BaseAppException):
    """Exception raised for authentication failures."""
    status_code = 401  # Unauthorized

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message)

class InvalidCredentialsError(AuthenticationError):
    """Exception raised for invalid credentials."""
    
    def __init__(self, message: str = "Invalid credentials provided"):
        super().__init__(message)

class AccountStatusError(AuthenticationError):
    """Exception raised for account status issues."""
    
    def __init__(self, message: str = "Account status issue"):
        super().__init__(message)

class UserNotVerifiedError(AccountStatusError):
    """Exception raised when a user's email is not verified."""
    
    def __init__(self, message: str = "User email not verified"):
        super().__init__(message)

class UserNotActiveError(AccountStatusError):
    """Exception raised when a user's account is not active."""
    
    def __init__(self, message: str = "User account is not active"):
        super().__init__(message)

class VerificationCodeError(BaseAppException):
    """Exception raised for verification failures."""
    status_code = 400  # Bad Request

    def __init__(self, message: str = "Verification failed"):
        super().__init__(message)

class VerificationCodeNotFoundError(VerificationCodeError):
    """Exception raised when verification code doesn't exist."""
    
    def __init__(self, email: str):
        super().__init__(f"No verification code found for email in database: {email}")
        self.email = email

class InvalidVerificationCodeError(VerificationCodeError):
    """Exception raised when the provided verification code is invalid."""
    
    def __init__(self, email: str):
        super().__init__(f"Invalid verification code provided for email: {email}")
        self.email = email
