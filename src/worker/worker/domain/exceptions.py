"""
Worker-specific exception hierarchy.

Exceptions are split into two categories:
- TransientWorkerError: Retryable failures (network, API timeouts, rate limits)
- PermanentWorkerError: Non-retryable failures (config, validation, logic errors)
"""


class WorkerError(Exception):
    """Base exception for all worker errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


# ── Transient (retryable) ──────────────────────────────────────────


class TransientWorkerError(WorkerError):
    """Base for retryable failures — network issues, API rate limits, etc."""


class AIServiceError(TransientWorkerError):
    """AI API timeout, rate limit, or temporary unavailability."""

    def __init__(self, detail: str = ""):
        super().__init__(f"AI service error: {detail}")


class StorageUploadError(TransientWorkerError):
    """Failed to upload to object storage (MinIO/S3)."""

    def __init__(self, detail: str = ""):
        super().__init__(f"Storage upload error: {detail}")


class ExternalAPIError(TransientWorkerError):
    """Generic external API failure (Pexels, ElevenLabs, etc.)."""

    def __init__(self, service: str, detail: str = ""):
        super().__init__(f"{service} API error: {detail}")


# ── Permanent (non-retryable) ─────────────────────────────────────


class PermanentWorkerError(WorkerError):
    """Base for non-retryable failures — config errors, invalid input, etc."""


class InvalidFormatError(PermanentWorkerError):
    """Requested video format does not exist."""

    def __init__(self, format_name: str):
        super().__init__(f"Invalid video format: '{format_name}'")


class MissingServiceError(PermanentWorkerError):
    """Required services are not available in the container."""

    def __init__(self, format_name: str, missing: list[str]):
        super().__init__(
            f"Format '{format_name}' requires missing services: {missing}"
        )


class WorkspaceSetupError(PermanentWorkerError):
    """Failed to create or configure the workspace directory."""

    def __init__(self, detail: str = ""):
        super().__init__(f"Workspace setup failed: {detail}")
