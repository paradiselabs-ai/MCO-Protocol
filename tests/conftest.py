"""
Test configuration for pytest
"""

import os
import sys
import pytest

# Add src directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Configure pytest
def pytest_configure(config):
    """Configure pytest."""
    # Add markers
    config.addinivalue_line("markers", "unit: mark a test as a unit test")
    config.addinivalue_line("markers", "integration: mark a test as an integration test")
    
# Create fixtures for common test resources
@pytest.fixture
def example_config_dir():
    """Fixture to provide path to example config directory."""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '../examples/research_assistant'))
