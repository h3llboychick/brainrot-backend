"""
Video format implementations.

Import this package to trigger auto-registration of all formats.
"""

from .registry import VideoFormatRegistry

# Import all format implementations to trigger @register decorators
# Add new formats here as they are created
try:
    from . import would_you_rather
except ImportError as e:
    import logging
    logging.warning(f"Failed to import would_you_rather format: {e}")

__all__ = ['VideoFormatRegistry', 'would_you_rather']
