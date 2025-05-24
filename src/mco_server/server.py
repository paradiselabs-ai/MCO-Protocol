"""
Main MCO Server module

Provides the core MCO Server class that coordinates configuration, state management,
orchestration, and framework adapters.
"""

from typing import Dict, Any, Optional, List, Union
import os
import uuid
import logging

from .config import ConfigManager
from .state import StateManager
from .orchestrator import Orchestrator
from .evaluator import SuccessCriteriaEvaluator
from .adapters import BaseAdapter, get_adapter_by_name
from .api import APIGateway

logger = logging.getLogger(__name__)

class MCOServer:
    """
    Main MCO Server class that coordinates all components of the orchestration system.
    
    This class serves as the primary entry point for using MCO Server, handling the
    initialization of all components and providing methods for starting and managing
    orchestrations.
    """
    
    def __init__(
        self,
        config_dir: Optional[str] = None,
        adapters: Optional[List[BaseAdapter]] = None,
        state_persistence: str = "memory",
        auto_detect: bool = False
    ):
        """
        Initialize the MCO Server.
        
        Args:
            config_dir: Optional directory containing MCO configuration files
            adapters: Optional list of adapter instances to register
            state_persistence: Type of state persistence ("memory", "file", "redis")
            auto_detect: Whether to auto-detect available frameworks
        """
        self.config_manager = ConfigManager()
        self.state_manager = StateManager(persistence_type=state_persistence)
        self.evaluator = SuccessCriteriaEvaluator()
        self.orchestrator = Orchestrator(
            config_manager=self.config_manager,
            state_manager=self.state_manager,
            evaluator=self.evaluator
        )
        
        # Initialize adapter registry
        self.adapters = {}
        
        # Register provided adapters
        if adapters:
            for adapter in adapters:
                self.register_adapter(adapter.get_name(), adapter)
        
        # Auto-detect frameworks if requested
        if auto_detect:
            self._auto_detect_frameworks()
        
        # Load configuration if provided
        if config_dir:
            self.load_configuration(config_dir)
        
        # Initialize API gateway
        self.api_gateway = APIGateway(self)
        
        logger.info("MCO Server initialized")
    
    def load_configuration(self, config_dir: str) -> None:
        """
        Load MCO configuration from a directory.
        
        Args:
            config_dir: Directory containing MCO configuration files
        """
        if not os.path.isdir(config_dir):
            raise ValueError(f"Configuration directory does not exist: {config_dir}")
        
        self.config_manager.load_from_directory(config_dir)
        logger.info(f"Loaded configuration from {config_dir}")
    
    def register_adapter(self, name: str, adapter: BaseAdapter) -> None:
        """
        Register a framework adapter.
        
        Args:
            name: Name of the adapter
            adapter: Adapter instance
        """
        self.adapters[name] = adapter
        logger.info(f"Registered adapter: {name}")
    
    def start_orchestration(
        self,
        config_dir: Optional[str] = None,
        adapter_name: str = "default",
        adapter_config: Optional[Dict[str, Any]] = None,
        initial_state: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a new orchestration.
        
        Args:
            config_dir: Directory containing MCO configuration files
            adapter_name: Name of the adapter to use
            adapter_config: Configuration for the adapter
            initial_state: Initial state for the orchestration
            
        Returns:
            Orchestration ID
        """
        # Load configuration if provided
        if config_dir:
            self.load_configuration(config_dir)
        
        # Get adapter
        adapter = self._get_adapter(adapter_name)
        
        # Initialize adapter
        if adapter_config:
            adapter.initialize(adapter_config)
        
        # Generate orchestration ID
        orchestration_id = str(uuid.uuid4())
        
        # Initialize state
        if initial_state:
            self.state_manager.initialize_state(orchestration_id, initial_state)
        
        # Start orchestration
        self.orchestrator.start_orchestration(orchestration_id, adapter)
        
        logger.info(f"Started orchestration: {orchestration_id}")
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
    
    def get_orchestration_status(self, orchestration_id: str) -> Dict[str, Any]:
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
        self.api_gateway.start_server(host, port)
        logger.info(f"API server started on {host}:{port}")
    
    def _get_adapter(self, adapter_name: str) -> BaseAdapter:
        """
        Get an adapter by name.
        
        Args:
            adapter_name: Name of the adapter
            
        Returns:
            Adapter instance
        """
        if adapter_name in self.adapters:
            return self.adapters[adapter_name]
        
        # Try to load adapter dynamically
        adapter = get_adapter_by_name(adapter_name)
        if adapter:
            self.register_adapter(adapter_name, adapter)
            return adapter
        
        raise ValueError(f"Adapter not found: {adapter_name}")
    
    def _auto_detect_frameworks(self) -> None:
        """
        Auto-detect available frameworks and register adapters.
        """
        # Try to import and register common frameworks
        frameworks_to_try = ["lmstudio", "agentgpt", "superexpert"]
        
        for framework in frameworks_to_try:
            try:
                adapter = get_adapter_by_name(framework)
                if adapter:
                    self.register_adapter(framework, adapter)
                    logger.info(f"Auto-detected framework: {framework}")
            except Exception as e:
                logger.debug(f"Could not auto-detect framework {framework}: {e}")
