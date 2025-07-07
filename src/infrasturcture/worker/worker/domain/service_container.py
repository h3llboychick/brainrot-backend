from typing import Dict, Any, Callable


class ServiceContainer:
    """
    Container providing access to all available services.
    
    Formats can request services they need by name.
    Supports both pre-instantiated services and lazy factories.
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._lazy_factories: Dict[str, Callable[[], Any]] = {}
    
    def register(self, name: str, service: Any) -> None:
        """
        Register a pre-instantiated service.
        
        Args:
            name: Service identifier
            service: Service instance
        """
        self._services[name] = service
    
    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """
        Register a lazy factory (instantiated on first access).
        
        Args:
            name: Service identifier
            factory: Function that creates the service
        """
        self._lazy_factories[name] = factory
    
    def get(self, name: str) -> Any:
        """
        Get a service by name.
        
        Args:
            name: Service identifier
            
        Returns:
            Service instance
            
        Raises:
            ValueError: If service is not registered
        """
        # Check if already instantiated
        if name in self._services:
            return self._services[name]
        
        # Check if we have a factory
        if name in self._lazy_factories:
            # Instantiate lazily and cache
            service = self._lazy_factories[name]()
            self._services[name] = service
            return service
        
        raise ValueError(f"Service '{name}' not registered in container")
    
    def has(self, name: str) -> bool:
        """
        Check if service is available.
        
        Args:
            name: Service identifier
            
        Returns:
            True if service exists, False otherwise
        """
        return name in self._services or name in self._lazy_factories
    
    def list_services(self) -> list[str]:
        """
        List all registered service names.
        
        Returns:
            List of service identifiers
        """
        return list(set(self._services.keys()) | set(self._lazy_factories.keys()))
