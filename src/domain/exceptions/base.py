class BaseAppException(Exception):
    """Base exception class for all application exceptions."""
    status_code = 500  # Default status code
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)