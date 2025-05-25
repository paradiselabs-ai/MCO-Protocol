# MCO Server

[![CI](https://github.com/paradiselabs-ai/mco-server/actions/workflows/ci.yml/badge.svg)](https://github.com/paradiselabs-ai/mco-server/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Model Configuration Orchestration (MCO) Server is a lightweight orchestration layer that makes AI agents dramatically more reliable by maintaining core requirements in persistent memory while strategically introducing implementation details at the right moments.

## Features

- **Framework Agnostic**: Works with LM Studio, AgentGPT, SuperExpert, and more
- **Syntactical Natural Language Programming (SNLP)**: Combines structured syntax with natural language for reliable agent guidance
- **Progressive Revelation**: Strategically introduces features and styles at the right moments in the workflow
- **Success Criteria Tracking**: Explicitly evaluates progress against defined success criteria
- **Persistent Memory**: Maintains core requirements throughout the entire process

## Quick Start

### Installation

```bash
pip install mco-server
```

### Basic Usage

```python
from mco_server import MCOServer

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

## Documentation

For detailed documentation, see the [docs](./docs) directory:

- [Integration Examples](./docs/integration_examples.md)
- [File Types](./docs/file_types.md)
- [Visual Setup Tool Design](./docs/visual_setup_tool_design.md)

## Examples

The [examples](./examples) directory contains sample MCO configurations for various use cases:

- [Research Assistant](./examples/research_assistant/)
- [Product Development](./examples/product_development/)
- [Code Generation](./examples/code_generation/)

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Contact

- Website: [https://paradiselabs.co](https://paradiselabs.co)
- Email: developers@paradiselabs.co
- Twitter: [@paradiselabs_ai](https://twitter.com/paradiselabs_ai)
- Discord: [https://discord.gg/uQ69vc4Agc](https://discord.gg/uQ69vc4Agc)
