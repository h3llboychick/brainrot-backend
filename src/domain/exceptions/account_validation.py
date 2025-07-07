from .base import BaseAppException


class NotFoundSocialAccountError(BaseAppException):
    """Exception raised when a social account is not found."""
    pass

class InvalidSocialAccountCredentialsError(BaseAppException):
    """Exception raised for invalid social account credentials."""
    pass

class ExpiredSocialAccountCredentialsError(BaseAppException):
    """Exception raised for expired social account credentials."""
    pass
