from src.domain.exceptions.base import BaseAppException


class VideoError(BaseAppException):
    """Base exception for video-related errors."""

    status_code = 400

    def __init__(self, message: str = "Video error"):
        super().__init__(message)


class VideoFormatNotFoundError(VideoError):
    """Raised when a requested video format does not exist."""

    status_code = 404

    def __init__(self, format_id: int):
        if format_id:
            super().__init__(f"Video format with ID {format_id} not found.")
        else:
            super().__init__("Video format not found.")
