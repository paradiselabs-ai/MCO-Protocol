# MCO Configuration Guide

This guide explains how to configure the MCO Protocol for your project, including server settings, adapter configuration, and API integration.

## Configuration Overview

MCO uses several configuration files to control its behavior:

1. **Server Configuration**: Controls the MCO server's behavior
2. **Adapter Configuration**: Configures specific adapters for different frameworks
3. **MCO Files**: Defines the orchestration logic (.core, .sc, .features, .styles)
4. **API Configuration**: Settings for the REST API (if used)

## Server Configuration

The MCO server is configured using a Python dictionary or a JSON file. Here's a complete example:

```python
server_config = {
    # General server settings
    "server": {
        "log_level": "INFO",  # DEBUG, INFO, WARNING, ERROR, CRITICAL
        "cache_dir": "/path/to/cache",  # Directory for caching (optional)
        "max_retries": 3,  # Maximum retries for failed operations
        "timeout": 30,  # Timeout in seconds for operations
    },
    
    # Orchestration settings
    "orchestration": {
        "progressive_revelation": True,  # Enable progressive revelation
        "evaluation_frequency": "step",  # When to evaluate: "step", "phase", or "end"
        "success_threshold": 0.8,  # Minimum success rate to continue (0.0 to 1.0)
        "max_steps": 100,  # Maximum number of steps in an orchestration
    },
    
    # Default adapter settings (can be overridden per orchestration)
    "default_adapter": {
        "name": "lmstudio",  # Default adapter to use
        "config": {
            "model_name": "gpt-3.5-turbo",  # Default model
            "temperature": 0.7,  # Default temperature
            "max_tokens": 1000,  # Default max tokens
        }
    }
}
```

You can load this configuration when initializing the MCO server:

```python
from mco_server import MCOServer

# Initialize with inline configuration
server = MCOServer(config=server_config)

# Or load from a JSON file
server = MCOServer.from_config_file("/path/to/config.json")
```

## Adapter Configuration

Each adapter has its own configuration options. Here are examples for supported adapters:

### LM Studio Adapter

```python
lmstudio_config = {
    "model_name": "gpt-3.5-turbo",  # Required: Model name in LM Studio
    "temperature": 0.7,  # Optional: Sampling temperature
    "max_tokens": 1000,  # Optional: Maximum tokens to generate
    "host": "localhost",  # Optional: LM Studio host
    "port": 1234,  # Optional: LM Studio port
}
```

### OpenAI Adapter (Example)

```python
openai_config = {
    "api_key": "your-api-key",  # Required: OpenAI API key
    "model_name": "gpt-4",  # Required: Model name
    "temperature": 0.7,  # Optional: Sampling temperature
    "max_tokens": 1000,  # Optional: Maximum tokens to generate
    "organization": "your-org-id",  # Optional: Organization ID
}
```

### Custom Adapter

For custom adapters, refer to the adapter's documentation for specific configuration options.

## MCO Files Configuration

MCO uses four file types to define orchestration logic:

### 1. Core File (mco.core)

Contains core functionality that stays in persistent memory:

```
# Core functionality
@data Research capability
>NLP The agent should be able to search for information on a given topic.

@data Analysis capability
>NLP The agent should be able to analyze and synthesize information from multiple sources.
```

### 2. Success Criteria File (mco.sc)

Defines criteria for evaluating progress:

```
# Success criteria
@data Comprehensive research
>NLP The research should cover multiple perspectives and sources.

@data Factual accuracy
>NLP All information provided must be factually accurate and verifiable.
```

### 3. Features File (mco.features)

Defines features to be progressively revealed:

```
# Features
@data Citation
>NLP All information should be properly cited with sources.

@data Key points
>NLP Each major section should include a summary of key points.
```

### 4. Styles File (mco.styles)

Specifies styling and presentation requirements:

```
# Styles
@data Format
>NLP The summary should be formatted with headings and bullet points.

@data Language
>NLP The language should be clear, concise, and accessible to a general audience.
```

## API Configuration

If you're using the MCO API wrapper, you can configure it using environment variables:

```bash
# Port to run the API server on
export MCO_API_PORT=8000

# Whether to require API key authentication
export MCO_API_KEY_REQUIRED=true

# API key for authentication when required
export MCO_API_KEY=your-api-key
```

Or when running with Docker:

```bash
docker run -p 8000:8000 \
  -e MCO_API_PORT=8000 \
  -e MCO_API_KEY_REQUIRED=true \
  -e MCO_API_KEY=your-api-key \
  mco-api
```

## Complete Example

Here's a complete example of using MCO with configuration:

```python
from mco_server import MCOServer

# Server configuration
server_config = {
    "server": {
        "log_level": "INFO",
    },
    "orchestration": {
        "progressive_revelation": True,
        "success_threshold": 0.8,
    },
    "default_adapter": {
        "name": "lmstudio",
        "config": {
            "model_name": "gpt-3.5-turbo",
        }
    }
}

# Initialize MCO Server
server = MCOServer(config=server_config)

# Start orchestration with specific adapter config
orchestration_id = server.start_orchestration(
    config_dir="./examples/research_assistant/",
    adapter_name="lmstudio",
    adapter_config={
        "model_name": "llama3-8b",
        "temperature": 0.5,
    }
)

# Run orchestration
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

## Troubleshooting

If you encounter configuration issues:

1. **Validation Errors**: Check that all required configuration keys are provided
2. **Adapter Errors**: Verify the adapter name is correct and the adapter is properly registered
3. **File Errors**: Ensure all MCO files are in the correct location and format
4. **API Errors**: Check environment variables and network settings

For more detailed troubleshooting, refer to the logs (set `log_level` to "DEBUG" for verbose output).
