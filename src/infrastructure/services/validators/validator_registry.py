from typing import Dict

from src.domain.enums import SocialPlatform
from src.domain.interfaces.services import ISocialAccountValidator


class ValidatorRegistry:
    _validators: Dict[str, ISocialAccountValidator] = {}
    _initialized: bool = False

    @classmethod
    def register(
        cls, platform: SocialPlatform, validator: ISocialAccountValidator
    ) -> None:
        """Register a validator for a platform"""
        cls._validators[platform.value] = validator

    @classmethod
    def _ensure_initialized(cls) -> None:
        if not cls._initialized:
            initialize_validators()

    @classmethod
    def get_validator(cls, platform: str) -> ISocialAccountValidator:
        """Get validator for a platform"""
        cls._ensure_initialized()
        validator = cls._validators.get(platform)
        if not validator:
            raise ValueError(
                f"No validator registered for platform: {platform}"
            )
        return validator

    @classmethod
    def has_validator(cls, platform: str) -> bool:
        """Check if validator exists for platform"""
        cls._ensure_initialized()
        return platform in cls._validators


def initialize_validators():
    from src.infrastructure.services.validators.youtube_validator import (
        youtube_validator,
    )

    ValidatorRegistry.register(SocialPlatform.youtube, youtube_validator)
    ValidatorRegistry._initialized = True
    # Add more platforms here as you implement them:
    # ValidatorRegistry.register(SocialPlatform.tiktok, tiktok_validator)
    # ValidatorRegistry.register(SocialPlatform.instagram, instagram_validator)
