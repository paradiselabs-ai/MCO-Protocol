"""
Main MCO Server module

Provides the core server functionality for MCO Server,
preserving the original Percertain DSL structure and progressive revelation approach.
"""

from typing import Dict, Any, Optional
import logging
import os
from .config import ConfigManager
from .state import StateManager
from .orchestrator import Orchestrator
from .evaluator import SuccessCriteriaEvaluator
from .adapters import BaseAdapter, get_adapter_by_name
from .api import APIGateway

logger = logging.getLogger(__name__)

class MCOServer:
    """
    Main MCO Server class.
    
    Coordinates all components and provides the main interface for MCO Server,
    preserving the original Percertain DSL structure and progressive revelation approach.
    """
    
    def __init__(self, state_dir: Optional[str] = None):
        """
        Initialize the MCO Server.
        
        Args:
            state_dir: Directory for storing state files (optional)
        """
        # Initialize components
        self.config_manager = ConfigManager()
        self.state_manager = StateManager(state_dir)
        self.evaluator = SuccessCriteriaEvaluator()
        self.orchestrator = Orchestrator(
            self.config_manager,
            self.state_manager,
            self.evaluator
        )
        self.api_gateway = APIGateway(
            self.config_manager,
            self.state_manager,
            self.orchestrator
        )
        
        # Initialize adapters registry
        self.adapters = {}
        
        logger.info("Initialized MCO Server")
    
    def register_adapter(self, name: str, adapter: BaseAdapter) -> None:
        """
        Register an adapter.
        
        Args:
            name: Name of the adapter
            adapter: Adapter instance
        """
        self.adapters[name] = adapter
        logger.info(f"Registered adapter: {name}")
    
    def start_orchestration(
        self,
        config_dir: str,
        adapter_name: str,
        adapter_config: Optional[Dict[str, Any]] = None,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a new orchestration.
        
        Args:
            config_dir: Directory containing MCO configuration files
            adapter_name: Name of the adapter to use
            adapter_config: Adapter configuration (optional)
            initial_state: Initial state variables (optional)
            
        Returns:
            Orchestration ID
        """
        # Load configuration
        self.config_manager.load_from_directory(config_dir)
        
        # Get adapter
        adapter = self.adapters.get(adapter_name)
        if not adapter:
            adapter = get_adapter_by_name(adapter_name)
            if not adapter:
                raise ValueError(f"Adapter not found: {adapter_name}")
        
        # Initialize adapter
        adapter.initialize(adapter_config or {})
        
        # Generate orchestration ID
        import uuid
        orchestration_id = str(uuid.uuid4())
        
        # Initialize state
        self.state_manager.initialize_state(orchestration_id, initial_state or {})
        
        # Start orchestration
        self.orchestrator.start_orchestration(orchestration_id, adapter)
        
        logger.info(f"Started orchestration {orchestration_id}")
        return orchestration_id
    
    def get_next_directive(self, orchestration_id: str) -> Dict[str, Any]:
        """
        Get the next directive for an orchestration.
        
        Args:
            orchestration_id: ID of the orchestration
            
        Returns:
            Directive dictionary
        """
        return self.orchestrator.get_next_directive(orchestration_id)
    
    def execute_directive(self, orchestration_id: str) -> Dict[str, Any]:
        """
        Execute the current directive for an orchestration.
        
        Args:
            orchestration_id: ID of the orchestration
            
        Returns:
            Result dictionary
        """
        return self.orchestrator.execute_current_directive(orchestration_id)
    
    def process_result(self, orchestration_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a result for an orchestration.
        
        Args:
            orchestration_id: ID of the orchestration
            result: Result dictionary
            
        Returns:
            Evaluation dictionary
        """
        return self.orchestrator.process_result(orchestration_id, result)
    
    def get_status(self, orchestration_id: str) -> Dict[str, Any]:
        """
        Get the status of an orchestration.
        
        Args:
            orchestration_id: ID of the orchestration
            
        Returns:
            Status dictionary
        """
        return self.orchestrator.get_status(orchestration_id)
    
    def start_api_server(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """
        Start the API server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        self.api_gateway.start(host, port)
