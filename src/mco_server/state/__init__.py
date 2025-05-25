"""
State Manager for MCO Server

This module provides functionality for managing orchestration state,
preserving the original Percertain DSL structure and progressive revelation approach.
"""

from typing import Dict, Any, Optional, List
import os
import json
import logging
import time

logger = logging.getLogger(__name__)

class StateManager:
    """
    Manages orchestration state for MCO Server.
    Preserves the progressive revelation structure and handles persistent vs. injected components.
    """
    
    def __init__(self, state_dir: Optional[str] = None):
        """
        Initialize the state manager.
        
        Args:
            state_dir: Directory for storing state files (optional)
        """
        self.state_dir = state_dir
        self.states = {}
        
        # Create state directory if it doesn't exist
        if self.state_dir and not os.path.exists(self.state_dir):
            os.makedirs(self.state_dir)
    
    def initialize_state(self, orchestration_id: str, initial_state: Dict[str, Any]) -> None:
        """
        Initialize state for an orchestration.
        
        Args:
            orchestration_id: ID of the orchestration
            initial_state: Initial state dictionary
        """
        # Create base state
        state = {
            "orchestration_id": orchestration_id,
            "status": "initialized",
            "current_step_index": 0,
            "completed_steps": [],
            "variables": initial_state,
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        # Store state
        self.states[orchestration_id] = state
        
        # Persist state if state_dir is set
        if self.state_dir:
            self._persist_state(orchestration_id)
        
        logger.debug(f"Initialized state for orchestration {orchestration_id}")
    
    def get_state(self, orchestration_id: str) -> Optional[Dict[str, Any]]:
        """
        Get state for an orchestration.
        
        Args:
            orchestration_id: ID of the orchestration
            
        Returns:
            State dictionary or None if not found
        """
        # Check if state is in memory
        if orchestration_id in self.states:
            return self.states[orchestration_id]
        
        # Try to load from disk if state_dir is set
        if self.state_dir:
            state_path = os.path.join(self.state_dir, f"{orchestration_id}.json")
            if os.path.exists(state_path):
                try:
                    with open(state_path, "r") as f:
                        state = json.load(f)
                    
                    # Store in memory
                    self.states[orchestration_id] = state
                    
                    return state
                except Exception as e:
                    logger.error(f"Error loading state for orchestration {orchestration_id}: {e}")
        
        return None
    
    def update_state(self, orchestration_id: str, updates: Dict[str, Any]) -> None:
        """
        Update state for an orchestration.
        
        Args:
            orchestration_id: ID of the orchestration
            updates: Dictionary of updates to apply
        """
        # Get current state
        state = self.get_state(orchestration_id)
        if not state:
            raise ValueError(f"No state found for orchestration {orchestration_id}")
        
        # Apply updates
        for key, value in updates.items():
            state[key] = value
        
        # Update timestamp
        state["updated_at"] = time.time()
        
        # Persist state if state_dir is set
        if self.state_dir:
            self._persist_state(orchestration_id)
        
        logger.debug(f"Updated state for orchestration {orchestration_id}")
    
    def mark_step_complete(self, orchestration_id: str, step_id: str) -> None:
        """
        Mark a step as complete.
        
        Args:
            orchestration_id: ID of the orchestration
            step_id: ID of the step
        """
        # Get current state
        state = self.get_state(orchestration_id)
        if not state:
            raise ValueError(f"No state found for orchestration {orchestration_id}")
        
        # Add step to completed steps if not already there
        if step_id not in state.get("completed_steps", []):
            state.setdefault("completed_steps", []).append(step_id)
        
        # Update timestamp
        state["updated_at"] = time.time()
        
        # Persist state if state_dir is set
        if self.state_dir:
            self._persist_state(orchestration_id)
        
        logger.debug(f"Marked step {step_id} as complete for orchestration {orchestration_id}")
    
    def set_current_step(self, orchestration_id: str, step_index: int) -> None:
        """
        Set the current step index.
        
        Args:
            orchestration_id: ID of the orchestration
            step_index: Index of the current step
        """
        # Get current state
        state = self.get_state(orchestration_id)
        if not state:
            raise ValueError(f"No state found for orchestration {orchestration_id}")
        
        # Set current step index
        state["current_step_index"] = step_index
        
        # Update timestamp
        state["updated_at"] = time.time()
        
        # Persist state if state_dir is set
        if self.state_dir:
            self._persist_state(orchestration_id)
        
        logger.debug(f"Set current step index to {step_index} for orchestration {orchestration_id}")
    
    def _persist_state(self, orchestration_id: str) -> None:
        """
        Persist state to disk.
        
        Args:
            orchestration_id: ID of the orchestration
        """
        if not self.state_dir:
            return
        
        state = self.states.get(orchestration_id)
        if not state:
            return
        
        state_path = os.path.join(self.state_dir, f"{orchestration_id}.json")
        
        try:
            with open(state_path, "w") as f:
                json.dump(state, f, indent=2)
            
            logger.debug(f"Persisted state for orchestration {orchestration_id}")
            
        except Exception as e:
            logger.error(f"Error persisting state for orchestration {orchestration_id}: {e}")
