"""
Framework Adapter Base and Registry

This module provides the base adapter class and adapter registry functionality.
"""

from typing import Dict, Any, Optional, Type, Callable
import importlib
import logging

logger = logging.getLogger(__name__)

class BaseAdapter:
    """
    Base class for framework adapters.
    
    All framework adapters must inherit from this class and implement its methods.
    """
    
    def __init__(self):
        """Initialize the adapter."""
        self.initialized = False
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the adapter with configuration.
        
        Args:
            config: Configuration dictionary
        """
        raise NotImplementedError("Adapter must implement initialize method")
    
    def execute_directive(self, directive: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an orchestration directive.
        
        Args:
            directive: Directive dictionary
            
        Returns:
            Result dictionary
        """
        raise NotImplementedError("Adapter must implement execute_directive method")
    
    def update_state(self, state: Dict[str, Any]) -> None:
        """
        Update the adapter state based on orchestration state.
        
        Args:
            state: State dictionary
        """
        raise NotImplementedError("Adapter must implement update_state method")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the adapter.
        
        Returns:
            Capabilities dictionary
        """
        raise NotImplementedError("Adapter must implement get_capabilities method")
    
    def get_name(self) -> str:
        """
        Get the name of the adapter.
        
        Returns:
            Adapter name
        """
        return self.__class__.__name__.lower().replace("adapter", "")


# Adapter registry
_adapter_registry: Dict[str, Type[BaseAdapter]] = {}

def register_adapter(name: str) -> Callable[[Type[BaseAdapter]], Type[BaseAdapter]]:
    """
    Decorator to register an adapter class.
    
    Args:
        name: Name of the adapter
        
    Returns:
        Decorator function
    """
    def decorator(cls: Type[BaseAdapter]) -> Type[BaseAdapter]:
        _adapter_registry[name] = cls
        logger.debug(f"Registered adapter: {name}")
        return cls
    return decorator

def get_adapter_by_name(name: str) -> Optional[BaseAdapter]:
    """
    Get an adapter instance by name.
    
    Args:
        name: Name of the adapter
        
    Returns:
        Adapter instance or None if not found
    """
    # Check if adapter is in registry
    if name in _adapter_registry:
        return _adapter_registry[name]()
    
    # Try to import adapter module
    try:
        module_name = f"mco_server.adapters.{name}"
        module = importlib.import_module(module_name)
        
        # Look for adapter class
        for attr_name in dir(module):
            if attr_name.lower().endswith("adapter"):
                adapter_class = getattr(module, attr_name)
                if isinstance(adapter_class, type) and issubclass(adapter_class, BaseAdapter):
                    return adapter_class()
    except (ImportError, AttributeError) as e:
        logger.debug(f"Could not load adapter {name}: {e}")
    
    return None
