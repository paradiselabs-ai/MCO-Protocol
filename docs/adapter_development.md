## Adapter Development

MCO supports multiple AI frameworks through adapters. Here's how to create a new adapter:

### Adapter Interface

All adapters must implement the `BaseAdapter` interface:

```python
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAdapter(ABC):
    """Base class for all MCO adapters."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the adapter with configuration."""
        self.config = config
    
    @abstractmethod
    def execute(self, directive: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a directive using the framework."""
        pass
    
    @abstractmethod
    def evaluate(self, result: Dict[str, Any], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a result against success criteria."""
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up any resources used by the adapter."""
        pass
```

### Example Adapter Implementation

Here's a simplified example of the LM Studio adapter:

```python
from mco_server.adapters.base import BaseAdapter
import lmstudio

class LMStudioAdapter(BaseAdapter):
    """Adapter for LM Studio."""
    
    def __init__(self, config):
        super().__init__(config)
        
        # Initialize LM Studio client
        self.client = lmstudio.llm(
            model_name=config.get("model_name"),
            host=config.get("host", "localhost"),
            port=config.get("port", 1234)
        )
        self.chat = lmstudio.Chat()
    
    def execute(self, directive):
        # Extract directive content
        content = directive.get("content", "")
        
        # Create system prompt
        system_prompt = "You are a helpful AI assistant."
        self.chat = lmstudio.Chat(system_prompt)
        
        # Add user message
        self.chat.add_user_message(content)
        
        # Generate response
        response = self.client.respond(self.chat)
        
        return {
            "result": response,
            "metadata": {
                "model": self.config.get("model_name")
            }
        }
    
    def evaluate(self, result, criteria):
        # Implementation of evaluation logic
        # ...
        
        return {
            "success": 0.9,
            "feedback": "Evaluation feedback"
        }
    
    def cleanup(self):
        self.client = None
        self.chat = None
```

### Registering an Adapter

To make your adapter available to MCO:

```python
from mco_server import MCOServer
from my_custom_adapter import MyCustomAdapter

# Initialize server
server = MCOServer()

# Register custom adapter
server.register_adapter("my_framework", MyCustomAdapter)

# Use the adapter
orchestration_id = server.start_orchestration(
    config_dir="./my_project/",
    adapter_name="my_framework",
    adapter_config={"model_name": "my-model"}
)
```

## Conclusion

MCO provides a structured approach to AI agent orchestration that dramatically improves reliability and output quality. By using progressive revelation, persistent vs. injected context, and explicit success criteria evaluation, MCO transforms simple LLM interfaces into powerful, reliable agent orchestration platforms.

For more information, examples, and updates, visit the [MCO Protocol GitHub repository](https://github.com/paradiselabs-ai/MCO-Protocol).
