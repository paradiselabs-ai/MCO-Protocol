# MCO Server Documentation

## Overview

This documentation provides comprehensive information about MCO Server, its architecture, configuration, and usage.

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture](#architecture)
3. [Configuration Files](#configuration-files)
4. [API Reference](#api-reference)
5. [Framework Adapters](#framework-adapters)
6. [Integration Guide](#integration-guide)

## Introduction

MCO Server is a framework-agnostic orchestration layer for reliable AI agent workflows. It provides a standardized way to orchestrate AI agents across different frameworks, ensuring reliable, high-quality outputs.

Unlike traditional "vibe coding" approaches where AI agents operate without clear guidance, MCO Server provides structured orchestration with explicit success criteria evaluation, dramatically improving reliability and output quality.

## Architecture

MCO Server follows a modular architecture with the following key components:

### Core Components

1. **Server**: The main entry point that coordinates all components
2. **Config Manager**: Loads and manages MCO configuration files
3. **State Manager**: Maintains orchestration state with persistence options
4. **Orchestrator**: Coordinates workflow execution and success criteria evaluation
5. **Evaluator**: Evaluates success criteria against execution results
6. **Adapters**: Framework-specific adapters for executing directives
7. **API Gateway**: REST API for interacting with MCO Server

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        MCO Server                           │
├─────────────┬─────────────┬─────────────┬─────────────┬─────┴─────┐
│             │             │             │             │           │
│ Config      │ State       │ Orchestrator│ Evaluator   │ API       │
│ Manager     │ Manager     │             │             │ Gateway   │
│             │             │             │             │           │
└─────────────┴─────────────┴──────┬──────┴─────────────┴───────────┘
                                   │
                                   ▼
                          ┌─────────────────┐
                          │ Adapter Registry│
                          └────────┬────────┘
                                   │
                 ┌─────────────────┼─────────────────┐
                 │                 │                 │
        ┌────────▼─────┐  ┌────────▼─────┐  ┌────────▼─────┐
        │ LM Studio    │  │ AgentGPT     │  │ SuperExpert  │
        │ Adapter      │  │ Adapter      │  │ Adapter      │
        └──────────────┘  └──────────────┘  └──────────────┘
```

## Configuration Files

MCO Server uses a set of configuration files to define orchestration behavior:

### mco.app

The main application configuration file that defines the workflow steps and overall behavior.

Example:
```
@workflow
{
  "name": "Research Assistant",
  "description": "An AI research assistant workflow",
  "steps": [
    {
      "id": "step_1",
      "name": "Understand Research Topic",
      "instruction": "Analyze the research topic and identify key areas to investigate",
      "success_condition": "topic_understanding"
    },
    {
      "id": "step_2",
      "name": "Gather Information",
      "instruction": "Search for relevant information about {{{topic}}}",
      "success_condition": "information_gathered"
    },
    {
      "id": "step_3",
      "name": "Synthesize Findings",
      "instruction": "Synthesize the gathered information into a coherent report",
      "success_condition": "synthesis_complete"
    }
  ]
}
```

### mco.sc

The success criteria configuration file that defines how to evaluate the success of each step.

Example:
```
@success_criteria
{
  "success_criteria": [
    {
      "id": "topic_understanding",
      "description": "Demonstrate understanding of the research topic",
      "evaluation": "The response must identify at least 3 key areas for investigation"
    },
    {
      "id": "information_gathered",
      "description": "Gather comprehensive information about the topic",
      "evaluation": "The response must include information from at least 3 different sources"
    },
    {
      "id": "synthesis_complete",
      "description": "Synthesize findings into a coherent report",
      "evaluation": "The response must include a structured report with introduction, findings, and conclusion"
    }
  ]
}
```

### mco.features

Optional file that defines features to be injected into the workflow.

Example:
```
@features
{
  "research_capabilities": [
    "web_search",
    "academic_database_access",
    "citation_management"
  ],
  "analysis_capabilities": [
    "data_visualization",
    "statistical_analysis",
    "comparative_review"
  ]
}
```

### mco.styles

Optional file that defines style preferences for the workflow outputs.

Example:
```
@styles
{
  "writing_style": "academic",
  "citation_style": "APA",
  "formatting": {
    "headings": "numbered",
    "tables": "minimal",
    "figures": "labeled"
  }
}
```

## API Reference

MCO Server provides a REST API for interacting with orchestrations:

### Start Orchestration

```
POST /api/v1/orchestration
```

Request body:
```json
{
  "config_dir": "/path/to/mco",
  "adapter_name": "lmstudio",
  "adapter_config": {
    "model_name": "qwen2.5-7b-instruct-1m"
  },
  "initial_state": {
    "topic": "quantum computing"
  }
}
```

Response:
```json
{
  "orchestration_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Get Next Directive

```
POST /api/v1/orchestration/{orchestration_id}/directive
```

Response:
```json
{
  "type": "execute",
  "step_id": "step_1",
  "instruction": "Analyze the research topic and identify key areas to investigate",
  "guidance": "You need to focus on: Demonstrate understanding of the research topic. Specifically, ensure that The response must identify at least 3 key areas for investigation",
  "step_index": 0,
  "total_steps": 3
}
```

### Execute Directive

```
POST /api/v1/orchestration/{orchestration_id}/execute
```

Response:
```json
{
  "result": {
    "output": "I've analyzed the quantum computing research topic and identified the following key areas to investigate:\n\n1. Quantum Algorithms\n2. Quantum Hardware\n3. Quantum Error Correction\n4. Quantum Machine Learning\n5. Quantum Cryptography",
    "metadata": {
      "model": "qwen2.5-7b-instruct-1m",
      "tokens": 128
    },
    "status": "success"
  },
  "evaluation": {
    "success": true,
    "feedback": "Success: The response identified 5 key areas for investigation, exceeding the requirement of 3",
    "progress": 0.33,
    "criterion_id": "topic_understanding",
    "details": {}
  }
}
```

### Get Orchestration Status

```
GET /api/v1/orchestration/{orchestration_id}
```

Response:
```json
{
  "orchestration_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "in_progress",
  "current_step_index": 1,
  "completed_steps": ["step_1"],
  "total_steps": 3,
  "progress": 0.33
}
```

## Framework Adapters

MCO Server supports multiple AI agent frameworks through adapters:

### LM Studio Adapter

Adapter for the LM Studio Python SDK.

```python
from mco_server import MCOServer
from mco_server.adapters.lmstudio import LMStudioAdapter

# Initialize server with LM Studio adapter
server = MCOServer()
server.register_adapter("lmstudio", LMStudioAdapter())

# Start orchestration
orchestration_id = server.start_orchestration(
    config_dir="./my_project/mco",
    adapter_name="lmstudio",
    adapter_config={
        "model_name": "qwen2.5-7b-instruct-1m",
        "system_prompt": "You are a helpful research assistant."
    }
)
```

### AgentGPT Adapter

Adapter for AgentGPT.

```python
from mco_server import MCOServer
from mco_server.adapters.agentgpt import AgentGPTAdapter

# Initialize server with AgentGPT adapter
server = MCOServer()
server.register_adapter("agentgpt", AgentGPTAdapter())

# Start orchestration
orchestration_id = server.start_orchestration(
    config_dir="./my_project/mco",
    adapter_name="agentgpt",
    adapter_config={
        "api_key": "your_api_key",
        "agent_type": "researcher"
    }
)
```

### SuperExpert Adapter

Adapter for SuperExpert.

```python
from mco_server import MCOServer
from mco_server.adapters.superexpert import SuperExpertAdapter

# Initialize server with SuperExpert adapter
server = MCOServer()
server.register_adapter("superexpert", SuperExpertAdapter())

# Start orchestration
orchestration_id = server.start_orchestration(
    config_dir="./my_project/mco",
    adapter_name="superexpert",
    adapter_config={
        "api_key": "your_api_key",
        "expert_type": "coder"
    }
)
```

## Integration Guide

### Basic Integration

```python
from mco_server import MCOServer

# Initialize server
server = MCOServer()

# Start orchestration
orchestration_id = server.start_orchestration(
    config_dir="./my_project/mco",
    adapter_name="lmstudio"
)

# Run orchestration loop
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

### API Server Integration

```python
from mco_server import MCOServer

# Initialize server
server = MCOServer()

# Start API server
server.start_api_server(host="0.0.0.0", port=8000)

print("MCO Server API running on http://0.0.0.0:8000")
```

### Docker Integration

```bash
# Build Docker image
docker build -t mco-server .

# Run Docker container
docker run -p 8000:8000 -v ./my_project/mco:/app/mco mco-server
```

### Framework-Specific Integration

See the [Framework Adapters](#framework-adapters) section for framework-specific integration examples.
