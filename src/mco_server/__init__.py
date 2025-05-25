"""
MCO Server - Model Configuration Orchestration Server

This module implements the persistent vs. injected component handling strategy
from the original Percertain DSL design, ensuring that:
1. Core and Success Criteria files are always in persistent memory/context
2. Features and Styles are injected at strategic points in the orchestration loop
"""

from typing import Dict, Any, Optional, List, Tuple
import logging
import os
import json
import uuid
from .config import ConfigManager
from .state import StateManager
from .orchestrator import Orchestrator
from .evaluator import SuccessCriteriaEvaluator
from .adapters import BaseAdapter, get_adapter_by_name

logger = logging.getLogger(__name__)

class PersistentMemoryManager:
    """
    Manages persistent memory for MCO orchestrations.
    
    Ensures that core and success criteria are always available in memory,
    while features and styles are only injected at strategic points.
    """
    
    def __init__(self):
        """Initialize the persistent memory manager."""
        self.persistent_memory = {}  # orchestration_id -> persistent memory
        self.injection_points = {}   # orchestration_id -> injection points
    
    def initialize_memory(self, orchestration_id: str, config_manager: ConfigManager) -> None:
        """
        Initialize persistent memory for an orchestration.
        
        Args:
            orchestration_id: ID of the orchestration
            config_manager: Configuration manager instance
        """
        # Extract persistent components (core + sc)
        persistent_memory = {
            "core": config_manager.get_core_config(),
            "success_criteria": config_manager.get_success_criteria(),
            "goal": config_manager.get_goal(),
            "target_audience": config_manager.get_target_audience(),
            "developer_vision": config_manager.get_developer_vision()
        }
        
        # Store persistent memory
        self.persistent_memory[orchestration_id] = persistent_memory
        
        # Define injection points based on workflow steps
        workflow_steps = config_manager.get_workflow_steps()
        injection_points = self._determine_injection_points(workflow_steps)
        self.injection_points[orchestration_id] = injection_points
        
        logger.debug(f"Initialized persistent memory for orchestration {orchestration_id}")
    
    def get_persistent_memory(self, orchestration_id: str) -> Dict[str, Any]:
        """
        Get persistent memory for an orchestration.
        
        Args:
            orchestration_id: ID of the orchestration
            
        Returns:
            Persistent memory dictionary
        """
        return self.persistent_memory.get(orchestration_id, {})
    
    def get_injected_components(
        self, 
        orchestration_id: str, 
        step_index: int, 
        config_manager: ConfigManager
    ) -> Dict[str, Any]:
        """
        Get injected components for a specific step.
        
        Args:
            orchestration_id: ID of the orchestration
            step_index: Index of the current step
            config_manager: Configuration manager instance
            
        Returns:
            Injected components dictionary
        """
        # Get injection points
        injection_points = self.injection_points.get(orchestration_id, {})
        
        # Initialize injected components
        injected_components = {}
        
        # Check if features should be injected at this step
        if "features" in injection_points and step_index in injection_points["features"]:
            injected_components["features"] = config_manager.get_features()
        
        # Check if styles should be injected at this step
        if "styles" in injection_points and step_index in injection_points["styles"]:
            injected_components["styles"] = config_manager.get_styles()
        
        return injected_components
    
    def _determine_injection_points(self, workflow_steps: List[Dict[str, Any]]) -> Dict[str, List[int]]:
        """
        Determine injection points for features and styles based on workflow steps.
        
        Args:
            workflow_steps: List of workflow step dictionaries
            
        Returns:
            Dictionary mapping component types to lists of step indices
        """
        injection_points = {
            "features": [],
            "styles": []
        }
        
        # Analyze workflow steps to determine appropriate injection points
        for i, step in enumerate(workflow_steps):
            step_id = step.get("id", "")
            task = step.get("task", "").lower()
            
            # Inject features for implementation/development steps
            if any(keyword in task for keyword in ["implement", "develop", "create", "build"]):
                injection_points["features"].append(i)
            
            # Inject styles for styling/formatting/presentation steps
            if any(keyword in task for keyword in ["style", "format", "present", "design"]):
                injection_points["styles"].append(i)
        
        # If no specific injection points were identified, use reasonable defaults
        if not injection_points["features"]:
            # Inject features at 1/3 of the way through the workflow
            feature_index = max(1, len(workflow_steps) // 3)
            injection_points["features"].append(feature_index)
        
        if not injection_points["styles"]:
            # Inject styles at 2/3 of the way through the workflow
            style_index = max(1, (len(workflow_steps) * 2) // 3)
            injection_points["styles"].append(style_index)
        
        return injection_points

class MCOServer:
    """
    Main MCO Server class with explicit persistent vs. injected component handling.
    
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
        
        # Initialize persistent memory manager
        self.memory_manager = PersistentMemoryManager()
        
        # Initialize adapters registry
        self.adapters = {}
        
        logger.info("Initialized MCO Server with persistent/injected component handling")
    
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
        Start a new orchestration with persistent memory initialization.
        
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
        orchestration_id = str(uuid.uuid4())
        
        # Initialize state
        self.state_manager.initialize_state(orchestration_id, initial_state or {})
        
        # Initialize persistent memory
        self.memory_manager.initialize_memory(orchestration_id, self.config_manager)
        
        # Start orchestration
        self.orchestrator.start_orchestration(orchestration_id, adapter)
        
        logger.info(f"Started orchestration {orchestration_id} with persistent memory")
        return orchestration_id
    
    def get_next_directive(self, orchestration_id: str) -> Dict[str, Any]:
        """
        Get the next directive for an orchestration with appropriate component injection.
        
        Args:
            orchestration_id: ID of the orchestration
            
        Returns:
            Directive dictionary
        """
        # Get base directive from orchestrator
        directive = self.orchestrator.get_next_directive(orchestration_id)
        
        # If directive is not an execution directive, return as is
        if directive.get("type") != "execute":
            return directive
        
        # Get current step index
        step_index = directive.get("step_index", 0)
        
        # Get persistent memory
        persistent_memory = self.memory_manager.get_persistent_memory(orchestration_id)
        
        # Get injected components for this step
        injected_components = self.memory_manager.get_injected_components(
            orchestration_id,
            step_index,
            self.config_manager
        )
        
        # Update directive with persistent memory and injected components
        directive["persistent_context"] = persistent_memory
        
        if injected_components:
            directive["injected_context"] = injected_components
            
            # Log which components are being injected
            component_types = list(injected_components.keys())
            logger.debug(f"Injecting components {component_types} at step {step_index}")
        
        return directive
    
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
        from .api import APIGateway
        api_gateway = APIGateway(
            self.config_manager,
            self.state_manager,
            self.orchestrator
        )
        api_gateway.start(host, port)
