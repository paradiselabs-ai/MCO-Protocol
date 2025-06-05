# Adapter Development Guide

This guide explains how to create new adapters for the MCO Protocol, allowing integration with different AI frameworks and LLM providers.

## What is an MCO Adapter?

An adapter connects the MCO orchestration layer to a specific AI framework or LLM provider. It translates MCO directives into framework-specific calls and handles the execution and evaluation of these directives.

## Adapter Structure

Each adapter consists of a Python class that inherits from the `BaseAdapter` abstract class and implements its methods:

- `__init__(self, config)`: Initialize the adapter with configuration
- `execute(self, directive)`: Execute a directive using the framework
- `evaluate(self, result, criteria)`: Evaluate a result against success criteria
- `cleanup(self)`: Clean up resources when the adapter is no longer needed

## Step-by-Step Guide to Creating a New Adapter

### 1. Create a New Adapter File

Create a new Python file in the `src/mco_server/adapters/` directory named after your framework (e.g., `openai.py` for OpenAI, `anthropic.py` for Anthropic).

```bash
touch src/mco_server/adapters/your_framework.py
```

### 2. Implement the Adapter Class

Copy the template below and customize it for your framework:

```python
from typing import Dict, Any
import logging

# Import base adapter class
from mco_server.adapters.base import BaseAdapter

# Set up logging
logger = logging.getLogger(__name__)

class YourFrameworkAdapter(BaseAdapter):
    """
    Adapter for YourFramework.
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.config = config
        
        # Validate required configuration
        self._validate_config()
        
        # Initialize your framework's client
        # self.client = YourFramework.Client(...)
        
        logger.info(f"Initialized YourFramework adapter")
    
    def _validate_config(self) -> None:
        required_keys = ["model_name"]  # Add any other required keys
        
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required configuration key: {key}")
    
    def execute(self, directive: Dict[str, Any]) -> Dict[str, Any]:
        # Implement execution logic
        pass
    
    def evaluate(self, result: Dict[str, Any], criteria: Dict[str, Any]) -> Dict[str, Any]:
        # Implement evaluation logic
        pass
    
    def cleanup(self) -> None:
        # Implement cleanup logic
        pass
```

### 3. Register Your Adapter

Open `src/mco_server/adapters/__init__.py` and add your adapter to the `ADAPTERS` dictionary:

```python
# Import your adapter
from mco_server.adapters.your_framework import YourFrameworkAdapter

# Add to registry
ADAPTERS = {
    "lmstudio": LMStudioAdapter,
    "your_framework": YourFrameworkAdapter,
    # Other adapters...
}
```

### 4. Implement the Execute Method

The `execute` method is the core of your adapter. It takes a directive from MCO and executes it using your framework:

```python
def execute(self, directive: Dict[str, Any]) -> Dict[str, Any]:
    logger.debug(f"Executing directive: {directive.get('type')}")
    
    # Extract directive content
    content = directive.get("content", "")
    directive_type = directive.get("type", "execute")
    
    # Execute using your framework
    response = self.client.generate(content)
    
    # Return the result
    return {
        "result": response,
        "metadata": {
            "directive_type": directive_type,
            "model": self.config.get("model_name"),
        }
    }
```

### 5. Implement the Evaluate Method

The `evaluate` method checks if a result meets the success criteria:

```python
def evaluate(self, result: Dict[str, Any], criteria: Dict[str, Any]) -> Dict[str, Any]:
    logger.debug("Evaluating result against criteria")
    
    # Extract result and criteria
    result_content = result.get("result", "")
    criteria_list = criteria.get("criteria", [])
    
    # Evaluate using your framework
    # This is a simplified example
    success_rate = 0.8  # Replace with actual evaluation
    
    return {
        "success": success_rate,
        "feedback": "Evaluation feedback",
        "details": [
            {"criterion": criterion, "met": True, "feedback": "Criterion met"}
            for criterion in criteria_list
        ]
    }
```

### 6. Test Your Adapter

Create a test script to verify your adapter works correctly:

```python
from mco_server.adapters import get_adapter

# Configure your adapter
config = {
    "model_name": "your-model-name",
    # Other configuration...
}

# Create adapter instance
adapter = get_adapter("your_framework", config)

# Test execution
result = adapter.execute({
    "content": "Test directive content",
    "type": "execute"
})
print(f"Execution result: {result}")

# Test evaluation
evaluation = adapter.evaluate(
    result,
    {"criteria": ["Test criterion"]}
)
print(f"Evaluation result: {evaluation}")

# Clean up
adapter.cleanup()
```

## Best Practices

1. **Error Handling**: Implement robust error handling to catch and report issues with your framework.
2. **Logging**: Use the logger to provide informative messages about adapter operations.
3. **Configuration Validation**: Validate all required configuration keys in the `_validate_config` method.
4. **Resource Management**: Properly initialize and clean up resources in `__init__` and `cleanup`.
5. **Documentation**: Add clear docstrings explaining your adapter's functionality and requirements.

## Example Adapters

For reference, see these example adapter implementations:

- `src/mco_server/adapters/lmstudio.py`: Adapter for LM Studio
- `src/mco_server/adapters/openai.py`: Adapter for OpenAI (if available)

## Troubleshooting

If you encounter issues with your adapter:

1. Check the logs for error messages
2. Verify your framework's client is properly initialized
3. Ensure all required configuration keys are provided
4. Test your framework's client independently to confirm it works

## Contributing

Once you've created and tested your adapter, consider contributing it back to the MCO Protocol repository:

1. Fork the repository
2. Create a branch for your adapter
3. Add your adapter implementation
4. Submit a pull request with a clear description of your adapter

For more information, see the [Contributing Guide](CONTRIBUTING.md).
