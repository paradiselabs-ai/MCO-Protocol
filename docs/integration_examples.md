# MCO Server Integration Documentation

## Overview

This document provides comprehensive documentation for integrating the MCO Server with various AI agent frameworks, based on our validation testing with the LM Studio Python SDK. The MCO Server maintains the original Syntactical Natural Language Programming (SNLP) approach while providing a robust server-based architecture for orchestrating AI agents.

## Integration Examples

### LM Studio Python SDK Integration

The LM Studio Python SDK offers the simplest integration path for MCO Server. Below is a complete integration example:

```python
from mco_server import MCOServer
from mco_server.adapters.lmstudio import LMStudioAdapter

# Initialize MCO Server
server = MCOServer()

# Start orchestration with LM Studio adapter
orchestration_id = server.start_orchestration(
    config_dir="./examples/research_assistant/",
    adapter_name="lmstudio",
    adapter_config={"model_name": "your-preferred-model"}
)

# Get the first directive
directive = server.get_next_directive(orchestration_id)

# Execute the directive
result = server.execute_directive(orchestration_id)

# Process the result
evaluation = server.process_result(orchestration_id, result)

# Continue orchestration until complete
while True:
    directive = server.get_next_directive(orchestration_id)
    
    if directive["type"] == "complete":
        print("Orchestration complete!")
        break
    
    result = server.execute_directive(orchestration_id)
    evaluation = server.process_result(orchestration_id, result)
    
    print(f"Step {directive['step_index'] + 1}/{directive['total_steps']} completed")
    print(f"Success: {evaluation['success']}")
```

### AgentGPT Integration

For AgentGPT integration, the approach is similar but requires connecting to the AgentGPT API:

```python
from mco_server import MCOServer
from mco_server.adapters.agentgpt import AgentGPTAdapter

# Initialize MCO Server
server = MCOServer()

# Start orchestration with AgentGPT adapter
orchestration_id = server.start_orchestration(
    config_dir="./examples/product_development/",
    adapter_name="agentgpt",
    adapter_config={
        "api_key": "your-agentgpt-api-key",
        "endpoint": "https://api.agentgpt.example/v1"
    }
)

# Continue with orchestration as in the LM Studio example
```

### SuperExpert Integration

SuperExpert integration follows the same pattern:

```python
from mco_server import MCOServer
from mco_server.adapters.superexpert import SuperExpertAdapter

# Initialize MCO Server
server = MCOServer()

# Start orchestration with SuperExpert adapter
orchestration_id = server.start_orchestration(
    config_dir="./examples/code_generation/",
    adapter_name="superexpert",
    adapter_config={
        "api_key": "your-superexpert-api-key",
        "model": "superexpert-pro"
    }
)

# Continue with orchestration as in the LM Studio example
```

## Key Findings from Validation Testing

Our validation testing with the LM Studio Python SDK revealed several important insights:

1. **Successful SNLP Preservation**: The server-based architecture successfully maintains the original Syntactical Natural Language Programming (SNLP) approach, with proper handling of both structured syntax and natural language components.

2. **Progressive Revelation Works**: The progressive revelation of features and styles at strategic points in the workflow is functioning correctly, with injected context appearing at the appropriate steps.

3. **Persistent Memory Handling**: Core configuration and success criteria are properly maintained in persistent memory throughout the orchestration process.

4. **Robust Error Handling**: The system correctly handles edge cases such as invalid configuration directories, non-existent adapters, and missing required parameters.

5. **State Management**: The state management system now properly maintains orchestration state across multiple steps, ensuring continuity and progress tracking.

## Integration Considerations

When integrating MCO Server with your framework, consider the following:

1. **Configuration Directory Structure**: Ensure your MCO configuration files (`mco.core`, `mco.sc`, `mco.features`, `mco.styles`) follow the standard format and are placed in a single directory.

2. **Adapter Requirements**: Each adapter has specific configuration requirements. Refer to the adapter documentation for details.

3. **Error Handling**: Implement proper error handling to catch and respond to exceptions that may occur during orchestration.

4. **State Persistence**: For production deployments, consider configuring a state directory to persist orchestration state across server restarts.

5. **Monitoring**: Implement logging and monitoring to track orchestration progress and identify any issues.

## Next Steps

Based on our validation testing, we recommend:

1. **Framework-Specific Adapters**: Develop and test adapters for additional frameworks to expand MCO Server compatibility.

2. **Visual Setup Tool**: Create a visual setup tool to simplify MCO configuration and integration.

3. **Performance Optimization**: Optimize the orchestration process for large-scale deployments.

4. **Documentation Expansion**: Expand documentation with more examples and best practices.

5. **Community Engagement**: Engage with the AI agent development community to gather feedback and improve MCO Server.
