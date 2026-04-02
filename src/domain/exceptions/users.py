from src.domain.exceptions.base import BaseAppException


class UserError(BaseAppException):
    """Base exception for user-related errors."""

    status_code = 400

    def __init__(self, message: str = "User error"):
        super().__init__(message)


class UserNotFoundError(UserError):
    """Raised when a requested user does not exist."""

    status_code = 404

    def __init__(self, user_id: str = "", email: str = ""):
        if user_id:
            super().__init__(f"User with ID {user_id} not found.")
        elif email:
            super().__init__(f"User with email {email} not found.")
        else:
            super().__init__("User not found.")


class UserAlreadyExistsError(UserError):
    """Raised when attempting to create a user that already exists."""

    status_code = 409

    def __init__(self, email: str):
        super().__init__(f"User with email {email} already exists.")


class InsufficientBalanceError(UserError):
    """Raised when a user does not have enough balance for an operation."""

    status_code = 402

    def __init__(self, message: str = "Insufficient balance"):
        super().__init__(message)
