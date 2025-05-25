"""
Test suite for MCO Server configuration manager
"""

import os
import pytest
import tempfile
from mco_server.config import ConfigManager

def test_load_from_directory():
    """Test loading configuration from a directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test files
        with open(os.path.join(temp_dir, "mco.core"), "w") as f:
            f.write("""
// --- mco.core --- 
@workflow "Test Workflow"
@description "A test workflow"
@version "1.0"

@data:
  test_data: "value"
  
@workflow_steps:
  step1:
    agent: "test_agent"
    task: "Test task"
    output: "test_output"
""")
        
        with open(os.path.join(temp_dir, "mco.sc"), "w") as f:
            f.write("""
// --- mco.sc --- 
@goal "Test goal"
@target_audience "Test audience"
@developer_vision "Test vision"

@success_criteria:
  - "Criterion 1"
  - "Criterion 2"
""")
        
        # Test loading
        config_manager = ConfigManager()
        config_manager.load_from_directory(temp_dir)
        
        # Verify core config
        core_config = config_manager.get_core_config()
        assert "workflow_steps" in core_config
        assert isinstance(core_config["workflow_steps"], dict)
        
        # Verify success criteria
        success_criteria = config_manager.get_success_criteria()
        assert 'goal "Test goal"' in success_criteria  # Fixed assertion
        
        # Verify workflow steps
        workflow_steps = config_manager.get_workflow_steps()
        assert len(workflow_steps) == 1
        assert workflow_steps[0]["id"] == "step1"

def test_get_workflow_steps():
    """Test getting workflow steps."""
    config_manager = ConfigManager()
    config_manager.core_config = {
        "workflow_steps": {
            "step1": {
                "agent": "test_agent",
                "task": "Test task"
            },
            "step2": {
                "agent": "test_agent2",
                "task": "Test task 2"
            }
        }
    }
    
    steps = config_manager.get_workflow_steps()
    assert len(steps) == 2
    assert steps[0]["id"] in ["step1", "step2"]
    assert steps[1]["id"] in ["step1", "step2"]
    assert steps[0]["id"] != steps[1]["id"]

def test_get_workflow_steps_empty():
    """Test getting workflow steps when none exist."""
    config_manager = ConfigManager()
    steps = config_manager.get_workflow_steps()
    assert len(steps) == 0

def test_get_workflow_steps_invalid():
    """Test getting workflow steps with invalid data."""
    config_manager = ConfigManager()
    config_manager.core_config = {
        "workflow_steps": "invalid string instead of dict"
    }
    
    steps = config_manager.get_workflow_steps()
    assert len(steps) == 0
