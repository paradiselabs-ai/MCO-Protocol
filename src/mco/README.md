# MCO Configuration Guide

This directory contains example MCO configuration files for a Research Assistant workflow. These files demonstrate how to use the Syntactical Natural Language Programming (SNLP) format to orchestrate AI agents with the MCO Protocol.

## Directory Contents

- `mco.core` - Core functionality that stays in persistent memory
- `mco.sc` - Success criteria that stays in persistent memory
- `mco.features` - Optional features injected at strategic points
- `mco.styles` - Styling preferences injected during formatting steps

## How to Use These Files

1. **Copy this directory**: Copy the entire `mco/` directory to your project
2. **Customize the files**: Edit each file to match your specific workflow needs
3. **Configure the MCO Server**: Point the server to this directory when starting

## Running the MCO Server

### Basic Usage

```python
from mco_server import MCOServer
from mco_server.adapters.lmstudio import LMStudioAdapter

# Initialize MCO Server
server = MCOServer()

# Register your preferred adapter
server.register_adapter("lmstudio", LMStudioAdapter())

# Start orchestration with your mco/ directory
orchestration_id = server.start_orchestration(
    config_dir="/path/to/your/mco",  # Path to this directory
    adapter_name="lmstudio",
    adapter_config={
        "model_name": "your-preferred-model"
    }
)

# Run the orchestration loop
while True:
    # Get next directive
    directive = server.get_next_directive(orchestration_id)
    
    if directive["type"] == "complete":
        print("Orchestration complete!")
        break
    
    print(f"\n--- Step: {directive['step_id']} ---")
    print(f"Instruction: {directive['instruction']}")
    
    # Execute directive
    result = server.execute_directive(orchestration_id)
    
    # Print evaluation
    evaluation = result["evaluation"]
    print(f"Success: {evaluation['success']}")
    print(f"Feedback: {evaluation['feedback']}")
    print(f"Progress: {evaluation['progress'] * 100:.0f}%")
```

### Running as an API Server

```python
from mco_server import MCOServer

# Initialize server
server = MCOServer()

# Register adapters
server.register_adapter("lmstudio", LMStudioAdapter())

# Start API server
server.start_api_server(
    host="0.0.0.0",
    port=8000,
    config_dir="/path/to/your/mco"  # Path to this directory
)

print("MCO Server API running on http://0.0.0.0:8000")
```

## Customizing for Your Workflow

### 1. Edit mco.core

- Update `@workflow` and `@description` with your workflow details
- Modify `@data` section with your specific data structures
- Define your own agents in the `@agents` section
- Create your workflow steps in the `@workflow_steps` section
- Add appropriate error handling in the `@error_handling` section

### 2. Edit mco.sc

- Update `@goal` with your workflow's overall goal
- Define your own success criteria with `@success_criteria`
- Specify your target audience with `@target_audience`
- Describe your vision with `@developer_vision`

### 3. Edit mco.features

- Add optional features with `@optional`
- Include brainstorming ideas with `@brainstorm`

### 4. Edit mco.styles

- Define styling preferences with `@style`

## SNLP Syntax Guide

MCO uses Syntactical Natural Language Programming (SNLP) with these key elements:

- `@marker` - Defines structured data or sections
- `>NLP` - Provides natural language context and guidance

Example:
```
@data Research capability
>NLP The agent should be able to search for information using available tools.
```

## How MCO Uses These Files

1. **Persistent Memory**: `mco.core` and `mco.sc` are loaded into persistent memory at the start of orchestration and are always available to the agents.

2. **Strategic Injection**: `mco.features` is injected during implementation/development steps, and `mco.styles` is injected during styling/formatting steps.

3. **Progressive Revelation**: Information is provided to agents in a structured, sequential manner to prevent overwhelming them with too much information at once.

For more detailed documentation, visit the [MCO Protocol GitHub repository](https://github.com/paradiselabs-ai/MCO-Protocol).
