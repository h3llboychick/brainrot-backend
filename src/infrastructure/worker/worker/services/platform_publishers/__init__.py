"""
Platform publishers package.

Imports all publisher implementations to trigger registration.
"""

# Import all publishers to trigger @register decorators
from .youtube import YouTubePublisher

__all__ = ['YouTubePublisher']
