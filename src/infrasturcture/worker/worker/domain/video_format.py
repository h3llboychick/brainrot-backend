from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

from .service_container import ServiceContainer


class VideoFormatStrategy(ABC):
    """
    Minimal interface for video format implementations.
    
    Formats have complete freedom over their internal workflow.
    The only requirements are:
    - Unique format_name
    - Workspace management (setup/cleanup)
    - Video generation from user settings
    """
    
    # ==================== IDENTITY ====================
    
    @property
    @abstractmethod
    def format_name(self) -> str:
        """
        Unique identifier for this format.
        
        Returns:
            Format identifier (e.g., "would_you_rather", "subway_surfers")
            
        Example:
            return "would_you_rather"
        """
        pass
    
    @property
    def required_services(self) -> list[str]:
        """
        List of service names this format needs from the container.
        
        Returns:
            List of service identifiers
            
        Example:
            return ['ai_client', 'voiceover', 'pexels', 'events_publisher']
        """
        return []
    
    # ==================== WORKSPACE MANAGEMENT ====================
    
    @abstractmethod
    def setup_workspace(self, job_id: str, base_dir: Path) -> Path:
        """
        Create workspace directory structure for this job.
        
        Format decides what directories/files to create.
        
        Args:
            job_id: Unique job identifier (use as directory name)
            base_dir: Base directory for all workspaces
            
        Returns:
            Path to workspace root directory
        """
        pass
    
    @abstractmethod
    def cleanup_workspace(self, workspace_root: Path) -> None:
        """
        Remove workspace and all temporary files.
        
        Called after generation completes (success or failure).
        
        Args:
            workspace_root: Root directory from setup_workspace()
        """
        pass
    
    # ==================== VIDEO GENERATION ====================
    
    @abstractmethod
    def generate(
        self,
        job_id: str,
        workspace_root: Path,
        format_settings: Dict[str, Any],
        services: ServiceContainer
    ) -> Path:
        """
        Generate complete video from start to finish.
        
        This is the main entry point. Format has COMPLETE CONTROL over:
        - Whether to use AI (and what prompts)
        - What assets to fetch (images, audio, video clips)
        - How to assemble the final video
        - Error handling and retry logic
        - Progress event publishing
        
        Args:
            job_id: Unique job identifier
            workspace_root: Workspace directory from setup_workspace()
            user_settings: Format-specific configuration from user
            services: ServiceContainer with available services
        
        Returns:
            URL of generated video filed saved to permanent storage.
            
        Raises:
            Exception: On generation failure
        """
        pass
