from src.domain.interfaces.services.social_account_validator import ISocialAccountValidator
from src.domain.enums.social_platform import SocialPlatform

from src.infrastructure.services.validators.youtube_validator import youtube_validator

from typing import Dict


class ValidatorRegistry: 
    _validators: Dict[str, ISocialAccountValidator] = {}
    
    @classmethod
    def register(cls, platform: SocialPlatform, validator: ISocialAccountValidator) -> None:
        """Register a validator for a platform"""
        cls._validators[platform.value] = validator
    
    @classmethod
    def get_validator(cls, platform: str) -> ISocialAccountValidator:
        """Get validator for a platform"""
        validator = cls._validators.get(platform)
        if not validator:
            raise ValueError(f"No validator registered for platform: {platform}")
        return validator
    
    @classmethod
    def has_validator(cls, platform: str) -> bool:
        """Check if validator exists for platform"""
        return platform in cls._validators


# Initialize registry
def initialize_validators():
    
    ValidatorRegistry.register(SocialPlatform.youtube, youtube_validator)
    
    # Add more platforms here as you implement them:
    # ValidatorRegistry.register(SocialPlatform.tiktok, tiktok_validator)
    # ValidatorRegistry.register(SocialPlatform.instagram, instagram_validator)


# Auto-initialize on import
initialize_validators()
