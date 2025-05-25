"""
Test suite for MCO Server state manager
"""

import os
import pytest
import tempfile
import json
from mco_server.state import StateManager

def test_initialize_state():
    """Test initializing state."""
    state_manager = StateManager()
    orchestration_id = "test-orchestration"
    initial_state = {"test_key": "test_value"}
    
    state_manager.initialize_state(orchestration_id, initial_state)
    
    state = state_manager.get_state(orchestration_id)
    assert state["orchestration_id"] == orchestration_id
    assert state["status"] == "initialized"
    assert state["current_step_index"] == 0
    assert state["completed_steps"] == []
    assert state["variables"]["test_key"] == "test_value"

def test_get_state_nonexistent():
    """Test getting state for a non-existent orchestration."""
    state_manager = StateManager()
    orchestration_id = "nonexistent-orchestration"
    
    state = state_manager.get_state(orchestration_id)
    
    # Should return a default state, not None
    assert state is not None
    assert state["orchestration_id"] == orchestration_id
    assert state["status"] == "unknown"
    assert state["current_step_index"] == 0
    assert state["completed_steps"] == []

def test_update_state():
    """Test updating state."""
    state_manager = StateManager()
    orchestration_id = "test-orchestration"
    
    # Initialize state
    state_manager.initialize_state(orchestration_id, {})
    
    # Update state
    updates = {"status": "running", "current_step_index": 1}
    state_manager.update_state(orchestration_id, updates)
    
    # Verify updates
    state = state_manager.get_state(orchestration_id)
    assert state["status"] == "running"
    assert state["current_step_index"] == 1

def test_mark_step_complete():
    """Test marking a step as complete."""
    state_manager = StateManager()
    orchestration_id = "test-orchestration"
    step_id = "test-step"
    
    # Initialize state
    state_manager.initialize_state(orchestration_id, {})
    
    # Mark step as complete
    state_manager.mark_step_complete(orchestration_id, step_id)
    
    # Verify step is marked as complete
    state = state_manager.get_state(orchestration_id)
    assert step_id in state["completed_steps"]

def test_set_current_step():
    """Test setting the current step."""
    state_manager = StateManager()
    orchestration_id = "test-orchestration"
    
    # Initialize state
    state_manager.initialize_state(orchestration_id, {})
    
    # Set current step
    state_manager.set_current_step(orchestration_id, 2)
    
    # Verify current step is set
    state = state_manager.get_state(orchestration_id)
    assert state["current_step_index"] == 2

def test_persist_state():
    """Test persisting state to disk."""
    with tempfile.TemporaryDirectory() as temp_dir:
        state_manager = StateManager(state_dir=temp_dir)
        orchestration_id = "test-orchestration"
        
        # Initialize state
        state_manager.initialize_state(orchestration_id, {"test_key": "test_value"})
        
        # Verify state file exists
        state_path = os.path.join(temp_dir, f"{orchestration_id}.json")
        assert os.path.exists(state_path)
        
        # Verify state file contents
        with open(state_path, "r") as f:
            state = json.load(f)
        
        assert state["orchestration_id"] == orchestration_id
        assert state["variables"]["test_key"] == "test_value"
