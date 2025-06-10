# MCO Protocol Hackathon - User Guide

## Introduction

Welcome to the MCO Protocol Hackathon submission! This guide will help you get started with the real end-to-end orchestration demo that showcases MCO as the missing orchestration layer for agent frameworks.

## What is MCO?

MCO (Model Configuration Orchestration) is a protocol that provides structured orchestration for AI agents using Syntactic Natural Language Programming (SNLP). It completes the "Agentic Trifecta" alongside MCP and A2P, solving key challenges in agent reliability through:

1. **Progressive Revelation**: Strategically reveal information to agents at the right time
2. **Structured Workflows**: Define clear steps and success criteria for agent tasks
3. **MCP Integration**: Works with any MCP-enabled framework with one line of config
4. **Visual Configuration**: Create SNLP files without learning syntax

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- Modal account with API key
- Anthropic API key for Claude

### Installation

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Install MCO Protocol:
   ```
   npm install @paradiselabs/mco-protocol
   ```

3. Set up environment variables:
   ```
   export ANTHROPIC_API_KEY=your_anthropic_api_key
   export MODAL_TOKEN_ID=your_modal_token_id
   export MODAL_TOKEN_SECRET=your_modal_token_secret
   ```

### Running the Demo

1. Start the application:
   ```
   python app.py
   ```

2. Open your browser and navigate to the provided URL (typically http://127.0.0.1:7860)

## Using the Demo

The demo consists of two main sections:

### 1. Agent Demo

This tab allows you to run the AutoGPT-like agent with real MCO orchestration:

1. Enter a task description in the "Task Description" field
2. Select a review type and language focus from the dropdowns
3. Optionally, enter code to review in the "Code to Review" field
4. Click "Run Agent" to start the agent with MCO orchestration
5. Watch the agent thinking process and MCO logs in real-time
6. View the results when the agent completes

### 2. SNLP Generator

This tab allows you to create and edit MCO workflow files:

1. Select a review type and language focus from the dropdowns
2. Click "Generate SNLP Files" to create initial files
3. Toggle between "Values Only" and "Full Edit" modes:
   - "Values Only": Edit just the values and NLP content
   - "Full Edit": Edit the entire file content
4. Make your changes to the files
5. Download individual files or all files as a zip

## Understanding the Components

### Modal Agent

The Modal implementation provides a real AutoGPT-like agent with:

- **LLM Interface**: Claude API for reasoning and planning
- **Tool System**: Code interpreter, file operations, web access
- **MCP Client**: Integration with MCO MCP server
- **Specialized Code Review**: Analysis, suggestions, and test generation

### MCO MCP Server

The MCO MCP server uses the official MCP SDK with stdio transport, ensuring compatibility with MCP Inspector and other MCP-enabled tools. Key features include:

- **Enhanced SNLP Parser**: Better cross-platform path handling and error reporting
- **Robust Error Handling**: Clear error messages and graceful failure modes
- **Proper Initialization**: Reliable startup and shutdown sequences

### SNLP Files

The system uses four SNLP files:

1. **mco.core**: Core workflow configuration
   - Defines the workflow, data variables, and agent steps
   - Always available to the agent as persistent memory

2. **mco.sc**: Success criteria
   - Defines goals, success criteria, target audience, and vision
   - Always available to the agent as persistent memory

3. **mco.features**: Feature specifications
   - Defines features to be implemented
   - Strategically injected during the workflow

4. **mco.styles**: Style guidelines
   - Defines style preferences
   - Strategically injected during the workflow

## Using MCO with Your Own Agent

1. Install the MCO package:
   ```
   npm install @paradiselabs/mco-protocol
   ```

2. Add MCO to your MCP config:
   ```json
   {
     "mcpServers": {
       "mco-orchestration": {
         "command": "node",
         "args": ["path/to/mco-mcp-server.js"],
         "env": {
           "MCO_CONFIG_DIR": "path/to/config"
         }
       }
     }
   }
   ```

3. Create SNLP files using the generator

4. Run your agent with MCO orchestration

## Troubleshooting

### Modal API Issues

- Ensure your Modal API key is correctly set
- Check that you have sufficient credits in your Modal account
- Verify your internet connection

### MCO Server Issues

- Make sure Node.js and npm are installed
- Check that the MCO package is installed
- Verify that the SNLP files exist in the config directory

### UI Issues

- Ensure Gradio is installed
- Try clearing your browser cache
- Check for JavaScript errors in the browser console

## Getting Help

If you encounter any issues or have questions, please:

1. Check the documentation in the `integration_documentation.md` file
2. Review the validation report in the `validation_report.md` file
3. Contact the development team through the hackathon platform

## License

This project is licensed under the MIT License - see the LICENSE file for details.
