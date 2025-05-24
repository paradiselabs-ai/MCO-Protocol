"""
State Manager for MCO Server

This module provides functionality for managing orchestration state.
"""

from typing import Dict, Any, Optional
import json
import os
import logging
import redis

logger = logging.getLogger(__name__)

class StateManager:
    """
    Manages orchestration state with different persistence options.
    """
    
    def __init__(self, persistence_type: str = "memory"):
        """
        Initialize the state manager.
        
        Args:
            persistence_type: Type of state persistence ("memory", "file", "redis")
        """
        self.persistence_type = persistence_type
        self.states = {}
        self.redis_client = None
        
        # Initialize persistence
        if persistence_type == "redis":
            self._initialize_redis()
        elif persistence_type == "file":
            os.makedirs(".mco_states", exist_ok=True)
        
        logger.info(f"Initialized state manager with {persistence_type} persistence")
    
    def initialize_state(self, orchestration_id: str, initial_state: Dict[str, Any]) -> None:
        """
        Initialize state for an orchestration.
        
        Args:
            orchestration_id: ID of the orchestration
            initial_state: Initial state dictionary
        """
        state = {
            "orchestration_id": orchestration_id,
            "current_step_index": 0,
            "completed_steps": [],
            "variables": initial_state or {},
            "status": "initialized"
        }
        
        self._save_state(orchestration_id, state)
        logger.debug(f"Initialized state for orchestration {orchestration_id}")
    
    def get_state(self, orchestration_id: str) -> Dict[str, Any]:
        """
        Get the current state for an orchestration.
        
        Args:
            orchestration_id: ID of the orchestration
            
        Returns:
            State dictionary
        """
        return self._load_state(orchestration_id)
    
    def update_state(self, orchestration_id: str, updates: Dict[str, Any]) -> None:
        """
        Update the state for an orchestration.
        
        Args:
            orchestration_id: ID of the orchestration
            updates: Dictionary of state updates
        """
        state = self._load_state(orchestration_id)
        
        # Apply updates
        for key, value in updates.items():
            if key == "variables":
                # Merge variables
                state["variables"].update(value)
            else:
                # Direct update
                state[key] = value
        
        self._save_state(orchestration_id, state)
        logger.debug(f"Updated state for orchestration {orchestration_id}")
    
    def set_variable(self, orchestration_id: str, name: str, value: Any) -> None:
        """
        Set a variable in the orchestration state.
        
        Args:
            orchestration_id: ID of the orchestration
            name: Variable name
            value: Variable value
        """
        state = self._load_state(orchestration_id)
        state["variables"][name] = value
        self._save_state(orchestration_id, state)
        logger.debug(f"Set variable {name} for orchestration {orchestration_id}")
    
    def get_variable(self, orchestration_id: str, name: str, default: Any = None) -> Any:
        """
        Get a variable from the orchestration state.
        
        Args:
            orchestration_id: ID of the orchestration
            name: Variable name
            default: Default value if variable not found
            
        Returns:
            Variable value or default
        """
        state = self._load_state(orchestration_id)
        return state["variables"].get(name, default)
    
    def mark_step_complete(self, orchestration_id: str, step_id: str) -> None:
        """
        Mark a step as complete in the orchestration state.
        
        Args:
            orchestration_id: ID of the orchestration
            step_id: ID of the completed step
        """
        state = self._load_state(orchestration_id)
        
        if step_id not in state["completed_steps"]:
            state["completed_steps"].append(step_id)
        
        self._save_state(orchestration_id, state)
        logger.debug(f"Marked step {step_id} as complete for orchestration {orchestration_id}")
    
    def is_step_complete(self, orchestration_id: str, step_id: str) -> bool:
        """
        Check if a step is complete in the orchestration state.
        
        Args:
            orchestration_id: ID of the orchestration
            step_id: ID of the step
            
        Returns:
            True if step is complete, False otherwise
        """
        state = self._load_state(orchestration_id)
        return step_id in state["completed_steps"]
    
    def set_current_step(self, orchestration_id: str, step_index: int) -> None:
        """
        Set the current step index in the orchestration state.
        
        Args:
            orchestration_id: ID of the orchestration
            step_index: Index of the current step
        """
        state = self._load_state(orchestration_id)
        state["current_step_index"] = step_index
        self._save_state(orchestration_id, state)
        logger.debug(f"Set current step index to {step_index} for orchestration {orchestration_id}")
    
    def get_current_step_index(self, orchestration_id: str) -> int:
        """
        Get the current step index from the orchestration state.
        
        Args:
            orchestration_id: ID of the orchestration
            
        Returns:
            Current step index
        """
        state = self._load_state(orchestration_id)
        return state.get("current_step_index", 0)
    
    def _initialize_redis(self) -> None:
        """Initialize Redis client for state persistence."""
        try:
            import redis
            self.redis_client = redis.Redis(
                host=os.environ.get("REDIS_HOST", "localhost"),
                port=int(os.environ.get("REDIS_PORT", 6379)),
                db=int(os.environ.get("REDIS_DB", 0)),
                password=os.environ.get("REDIS_PASSWORD", None)
            )
            self.redis_client.ping()  # Test connection
            logger.info("Connected to Redis for state persistence")
        except (ImportError, redis.ConnectionError) as e:
            logger.error(f"Failed to initialize Redis: {e}")
            logger.warning("Falling back to memory persistence")
            self.persistence_type = "memory"
    
    def _save_state(self, orchestration_id: str, state: Dict[str, Any]) -> None:
        """
        Save state to the configured persistence.
        
        Args:
            orchestration_id: ID of the orchestration
            state: State dictionary
        """
        if self.persistence_type == "memory":
            self.states[orchestration_id] = state
        elif self.persistence_type == "file":
            file_path = os.path.join(".mco_states", f"{orchestration_id}.json")
            with open(file_path, "w") as f:
                json.dump(state, f)
        elif self.persistence_type == "redis" and self.redis_client:
            self.redis_client.set(f"mco:state:{orchestration_id}", json.dumps(state))
    
    def _load_state(self, orchestration_id: str) -> Dict[str, Any]:
        """
        Load state from the configured persistence.
        
        Args:
            orchestration_id: ID of the orchestration
            
        Returns:
            State dictionary
        """
        if self.persistence_type == "memory":
            return self.states.get(orchestration_id, {"variables": {}})
        elif self.persistence_type == "file":
            file_path = os.path.join(".mco_states", f"{orchestration_id}.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    return json.load(f)
            return {"variables": {}}
        elif self.persistence_type == "redis" and self.redis_client:
            state_json = self.redis_client.get(f"mco:state:{orchestration_id}")
            if state_json:
                return json.loads(state_json)
            return {"variables": {}}
        return {"variables": {}}
