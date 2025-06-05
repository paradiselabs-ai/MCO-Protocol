"""
MCO Base Adapter

This file defines the BaseAdapter abstract class that all MCO adapters must implement.
It serves as the interface between the MCO orchestration layer and specific AI frameworks.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class BaseAdapter(ABC):
    """
    Abstract base class for all MCO adapters.
    
    All framework-specific adapters must inherit from this class and implement
    its abstract methods.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the adapter with the provided configuration.
        
        Args:
            config: Configuration dictionary with framework-specific settings
        """
        self.config = config
    
    @abstractmethod
    def execute(self, directive: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a directive using the framework.
        
        Args:
            directive: Dictionary containing the directive to execute
        
        Returns:
            Dictionary containing the execution result
        """
        pass
    
    @abstractmethod
    def evaluate(self, result: Dict[str, Any], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a result against success criteria.
        
        Args:
            result: Dictionary containing the result to evaluate
            criteria: Dictionary containing the success criteria
        
        Returns:
            Dictionary containing the evaluation result
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up any resources used by the adapter.
        """
        pass
