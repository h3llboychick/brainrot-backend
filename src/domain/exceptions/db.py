from src.domain.exceptions.base import BaseAppException


class DBError(BaseAppException):
    pass


class UserAlreadyExistsError(DBError):
    def __init__(self, email: str):
        super().__init__(f"User with email {email} already exists.")


class UserNotFoundError(DBError):
    def __init__(self, user_id: str = "", email: str = ""):
        if user_id:
            super().__init__(f"User with ID {user_id} not found.")
        elif email:
            super().__init__(f"User with email {email} not found.")
        else:
            super().__init__("User not found.")
