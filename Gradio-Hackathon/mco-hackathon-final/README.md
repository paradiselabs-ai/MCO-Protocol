# MCO Protocol Hackathon Submission

## Real AutoGPT Agent with MCO Orchestration

This project demonstrates the power of MCO (Model Configuration Orchestration) as the missing orchestration layer for agent frameworks. It features a real AutoGPT-like agent built with Modal API that is orchestrated by the MCO MCP server, with a single-page UI showing the agent's thinking process and orchestration logs.

## Key Features

- **Real Modal API Integration**: Genuine LLM inference with Claude
- **Real MCO Orchestration**: Using the actual MCO MCP server (not simulated)
- **Single-Page UI**: Shows Claude's thinking process and MCO orchestration logs
- **Visual SNLP Generator**: Edit values and NLP with a simple toggle
- **Code Review Agent**: Specialized for analyzing and improving code

## Project Structure

- `main.py`: Main entry point that integrates all components
- `modal_implementation.py`: AutoGPT-like agent implementation using Modal
- `gradio_ui.py`: Single-page Gradio UI for demonstration
- `mco-config/`: Directory containing SNLP files for orchestration
- `knowledge_graph.md`: Research on Modal, MCO, and Gradio integration
- `modal_agent_design.md`: Detailed design of the Modal agent
- `integration_documentation.md`: Documentation of the complete system

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 14+
- Modal account with API key
- Anthropic API key for Claude

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/mco-hackathon.git
   cd mco-hackathon
   ```

2. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install MCO Protocol:
   ```
   npm install @paradiselabs/mco-protocol
   ```

4. Set up environment variables:
   ```
   export ANTHROPIC_API_KEY=your_anthropic_api_key
   export MODAL_TOKEN_ID=your_modal_token_id
   export MODAL_TOKEN_SECRET=your_modal_token_secret
   ```

### Running the Demo

1. Start the application:
   ```
   python main.py
   ```

2. Open your browser and navigate to the provided URL

3. Use the Agent Demo tab to run the agent with MCO orchestration

4. Use the SNLP Generator tab to create and edit MCO workflow files

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

## Why MCO?

MCO completes the "Agentic Trifecta" alongside MCP and A2P, providing the missing orchestration layer for truly agentic AI. It solves key challenges in agent reliability through:

1. **Progressive Revelation**: Strategically reveal information to agents at the right time
2. **Structured Workflows**: Define clear steps and success criteria for agent tasks
3. **MCP Integration**: Works with any MCP-enabled framework with one line of config
4. **Visual Configuration**: Create SNLP files without learning syntax

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- The Modal team for their excellent serverless compute platform
- The Anthropic team for Claude API
- The MCP community for the Model Context Protocol
- The Gradio team for their UI framework
