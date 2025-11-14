from typing import Dict, Type
from celery.utils.log import get_logger

from ...domain.video_format import VideoFormatStrategy

logger = get_logger(__name__)


class VideoFormatRegistry:
    """
    Central registry for all available video format implementations.
    
    Usage:
        # Registration (in format module):
        @VideoFormatRegistry.register
        class MyFormat(VideoFormatStrategy):
            ...
        
        # Or manual registration:
        VideoFormatRegistry.register_format(MyFormat)
        
        # Retrieval:
        format_strategy = VideoFormatRegistry.get_format("my_format")
        
        # Discovery:
        all_formats = VideoFormatRegistry.list_formats()
    """
    
    _formats: Dict[str, Type[VideoFormatStrategy]] = {}
    
    @classmethod
    def register(cls, format_class: Type[VideoFormatStrategy]) -> Type[VideoFormatStrategy]:
        """
        Decorator to register a format class.
        
        Args:
            format_class: Video format strategy class
            
        Returns:
            The same class (allows use as decorator)
            
        Example:
            @VideoFormatRegistry.register
            class WouldYouRatherFormat(VideoFormatStrategy):
                ...
        """
        cls.register_format(format_class)
        return format_class
    
    @classmethod
    def register_format(cls, format_class: Type[VideoFormatStrategy]) -> None:
        """
        Manually register a format class.
        
        Args:
            format_class: Video format strategy class
            
        Raises:
            ValueError: If format_name conflicts with existing format
        """
        # Instantiate temporarily to get format_name
        try:
            instance = format_class()
            format_name = instance.format_name
        except Exception as e:
            logger.error(f"Failed to instantiate format class {format_class.__name__}: {e}")
            raise ValueError(f"Format class {format_class.__name__} must be instantiable: {e}")
        
        # Check for conflicts
        if format_name in cls._formats:
            existing_class = cls._formats[format_name]
            if existing_class is not format_class:
                raise ValueError(
                    f"Format name '{format_name}' already registered "
                    f"by {existing_class.__name__}. Cannot register {format_class.__name__}."
                )
            # Already registered, skip
            return
        
        cls._formats[format_name] = format_class
        logger.info(f"Registered video format: '{format_name}' ({format_class.__name__})")
    
    @classmethod
    def get_format(cls, format_name: str) -> VideoFormatStrategy:
        """
        Get a format strategy instance by name.
        
        Args:
            format_name: Format identifier (e.g., "would_you_rather")
            
        Returns:
            New instance of the format strategy
            
        Raises:
            ValueError: If format_name is not registered
        """
        if format_name not in cls._formats:
            available = ", ".join(cls.list_formats())
            raise ValueError(
                f"Unknown video format: '{format_name}'. "
                f"Available formats: {available or 'none'}"
            )
        
        format_class = cls._formats[format_name]
        return format_class()
    
    @classmethod
    def list_formats(cls) -> list[str]:
        """
        Get list of all registered format names.
        
        Returns:
            List of format identifiers
        """
        return sorted(cls._formats.keys())
    
    @classmethod
    def is_registered(cls, format_name: str) -> bool:
        """
        Check if a format is registered.
        
        Args:
            format_name: Format identifier
            
        Returns:
            True if format is registered, False otherwise
        """
        return format_name in cls._formats
    
    @classmethod
    def clear(cls) -> None:
        """
        Clear all registered formats.
        
        Mainly useful for testing.
        """
        cls._formats.clear()
        logger.info("Cleared all registered video formats")
