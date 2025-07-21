# 🚀 MCO Protocol: The Missing Orchestration Layer for MCP

<div align="center">

[![NPM Version](https://img.shields.io/npm/v/@paradiselabs/mco-protocol.svg)](https://www.npmjs.com/package/@paradiselabs/mco-protocol)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Hackathon](https://img.shields.io/badge/🏆-MCP%20Hackathon%202025-gold)](https://huggingface.co/Agents-MCP-Hackathon)

**Completing the Agentic Trifecta: MCP + A2P + MCO**

*Transform unreliable agents into structured, autonomous workflows with progressive revelation and persistent memory.*

[🎮 **Live Demo**](https://huggingface.co/spaces/paradiselabs/mco-protocol-demo) • [📦 **NPM Package**](https://www.npmjs.com/package/@paradiselabs/mco-protocol) • [📖 **Documentation**](https://github.com/paradiselabs-ai/MCO-Protocol/blob/main/docs)

</div>


## 🌟 The Agentic Trifecta

```mermaid
graph TB
    subgraph "The Foundation of Autonomous AI"
        MCP[📊 MCP<br/>Model Context Protocol<br/><i>Data Integration</i>]
        A2P[🤝 A2P<br/>Agent-to-Agent Protocol<br/><i>Communication</i>]
        MCO[🎛️ MCO<br/>Model Configuration Orchestration<br/><i>Reliable Orchestration</i>]
    end
    
    MCP --> AGENT[🤖 Autonomous Agent]
    A2P --> AGENT
    MCO --> AGENT
    
    AGENT --> RESULT[✨ Production-Ready<br/>Autonomous AI]
    
    style MCO fill:#667eea,stroke:#333,stroke-width:3px,color:#fff
    style RESULT fill:#2ecc71,stroke:#333,stroke-width:2px,color:#fff
```

**Why MCO is Essential:**
- 📊 **MCP** connects agents to data sources → *"What can I access?"*
- 🤝 **A2P** enables agent communication → *"How do we coordinate?"*  
- 🎛️ **MCO** ensures reliable execution → *"How do we actually get things done?"*

## 🎯 The Problem MCO Solves

Traditional autonomous agents (AutoGPT, BabyAGI) suffer from:
- 🔄 **Endless loops** and failed executions
- 🧠 **Context overload** leading to poor decisions  
- 🎯 **Lack of focus** on core objectives
- 📉 **Unpredictable reliability** in production

## 💡 The MCO Solution: Progressive Revelation

```mermaid
graph LR
    subgraph "Traditional Approach"
        T1[Agent] --> T2[Everything at Once<br/>📚 Core + Features + Styles + Context]
        T2 --> T3[❌ Overwhelmed<br/>Loops & Failures]
    end
    
    subgraph "MCO Progressive Revelation"
        M1[Agent] --> M2[🧠 Persistent Memory<br/>Core + Success Criteria]
        M2 --> M3[⚡ Step 1: Focus on Core]
        M3 --> M4[✨ Step 2: + Features Injection]
        M4 --> M5[🎨 Step 3: + Styles Injection]
        M5 --> M6[✅ Reliable Completion]
    end
    
    style T3 fill:#e74c3c,color:#fff
    style M6 fill:#2ecc71,color:#fff
```

## 🛠️ How MCO Works

### SNLP (Syntactic Natural Language Programming)

MCO uses a revolutionary programming language that combines structured syntax with natural language:

```yaml
# mco.core - Always in persistent memory
@workflow "Research Assistant"
>NLP An AI assistant that conducts autonomous research with reliability.

@data:
  topic: "AI Agent Orchestration"
  findings: []

@agents:
  researcher:
    steps:
      - "Research the topic thoroughly"
      - "Analyze patterns and insights"  
      - "Create comprehensive report"

# mco.features - Injected at 33% progress
@feature "Data Visualization"
>NLP Create charts and graphs when appropriate to enhance understanding.

# mco.styles - Injected at 66% progress  
@style "Professional Formatting"
>NLP Use clear headings, bullet points, and executive summary format.
```

### Orchestration Flow

```mermaid
sequenceDiagram
    participant AF as Agent Framework
    participant MCO as MCO MCP Server
    participant SNLP as SNLP Files
    
    Note over AF,SNLP: Progressive Revelation in Action
    
    AF->>MCO: start_orchestration()
    MCO->>SNLP: Load mco.core + mco.sc
    MCO-->>AF: orchestration_id
    
    AF->>MCO: get_next_directive()
    Note right of MCO: Persistent Memory Only
    MCO-->>AF: Step 1 + Core Context
    
    AF->>MCO: complete_step(result)
    MCO->>MCO: Evaluate against success criteria
    
    AF->>MCO: get_next_directive()
    Note right of MCO: Strategic Injection
    MCO->>SNLP: Inject mco.features
    MCO-->>AF: Step 2 + Core + Features
    
    AF->>MCO: complete_step(result)
    
    AF->>MCO: get_next_directive()
    MCO->>SNLP: Inject mco.styles  
    MCO-->>AF: Step 3 + Core + Features + Styles
    
    AF->>MCO: complete_step(result)
    MCO-->>AF: ✅ Workflow Complete
```

## 🚀 Quick Start

### Installation

```bash
npm install -g @paradiselabs/mco-protocol
```

### Create Your First Workflow

```bash
# Initialize new MCO project
mco init my-research-assistant

# Opens configuration tool in browser
# Generates: mco.core, mco.sc, mco.features, mco.styles
```

### Add to Any MCP-Enabled Framework

Note: the directory mco-config is the directory which holds the four orchestration files, written in SNLP. This should go in your project directory. thus, the tool is able to be used even for IDE coding agent extensions or integrated coding agents, so long as the root of the current project contains a directory titled "mco-config/" and inside it contains the SNLP orchestration workflow files. 

```json
{
  "mcpServers": {
    "mco-orchestration": {
      "command": "npx",
      "args": ["@paradiselabs/mco-protocol", "serve", "./mco-config"]
    }
  }
}
```

### Use in Your Agent Framework

```python
# Works with ANY MCP-enabled framework
directive = mcp_client.call_tool("get_next_directive")
result = execute_task(directive.instruction)
mcp_client.call_tool("complete_step", step_id=directive.step_id, result=result)
```

## 🎭 Live Demo

**🎮 [Try the Interactive Demo](https://huggingface.co/spaces/paradiselabs/mco-protocol-demo)**

Generate real SNLP configurations and see MCO in action with live MCP server simulation.

## 📊 Architecture Overview

```mermaid
graph TB
    subgraph "MCO MCP Server"
        CLI[🖥️ CLI Interface<br/>mco init, serve, validate]
        CONFIG[🎛️ Configuration Tool<br/>Web-based SNLP Generator]
        PARSER[📝 SNLP Parser<br/>@markers + >NLP sections]
        ENGINE[⚡ Orchestration Engine<br/>Progressive Revelation]
        MCP[📡 MCP Tool Provider<br/>start_orchestration, get_next_directive]
    end
    
    subgraph "SNLP Files"
        CORE[🧠 mco.core<br/>Persistent Memory]
        SC[🎯 mco.sc<br/>Success Criteria]  
        FEATURES[✨ mco.features<br/>Strategic Injection]
        STYLES[🎨 mco.styles<br/>Strategic Injection]
    end
    
    subgraph "Agent Frameworks"
        AUTOGPT[🤖 AutoGPT]
        CREWAI[👥 CrewAI]
        LANGGRAPH[🕸️ LangGraph]
        CUSTOM[⚙️ Custom Agents]
    end
    
    CLI --> CONFIG
    CONFIG --> CORE & SC & FEATURES & STYLES
    PARSER --> CORE & SC & FEATURES & STYLES
    PARSER --> ENGINE
    ENGINE --> MCP
    
    MCP <==> AUTOGPT
    MCP <==> CREWAI  
    MCP <==> LANGGRAPH
    MCP <==> CUSTOM
    
    style MCO fill:#667eea,color:#fff
    style CORE fill:#e8f5e9
    style SC fill:#e3f2fd
    style FEATURES fill:#fff3e0
    style STYLES fill:#fce4ec
```

## 🏆 Perfect for MCP Hackathon 2025

**Track 1: MCP Server Implementation** ✅

MCO exemplifies the future of MCP by:
- 🔧 **Extending MCP's Vision**: Making agent orchestration as standardized as data access
- 🎯 **Solving Real Problems**: Transforming unreliable agents into production-ready systems
- 🚀 **Ready for Production**: Live NPM package, working implementation
- 🌟 **Innovative Approach**: First orchestration protocol designed specifically for MCP ecosystem

## 📈 Before vs After

```mermaid
graph LR
    subgraph "Before MCO"
        B1[🤖 Agent] --> B2[❓ Vague Prompts]
        B2 --> B3[🔄 Loops & Failures]
        B3 --> B4[😤 Manual Intervention]
    end
    
    subgraph "After MCO"
        A1[🤖 Agent] --> A2[🎛️ MCO Orchestration]
        A2 --> A3[📋 Structured Steps]
        A3 --> A4[✅ Reliable Completion]
    end
    
    style B3 fill:#e74c3c,color:#fff
    style A4 fill:#2ecc71,color:#fff
```

## 🔗 Available MCP Tools

MCO exposes these tools through the MCP protocol:

| Tool | Description | Use Case |
|------|-------------|----------|
| `start_orchestration` | Initialize new workflow | Begin autonomous task |
| `get_next_directive` | Get next step with context | Progressive execution |
| `complete_step` | Mark step complete | Track progress |
| `get_workflow_status` | Check progress | Monitoring |
| `evaluate_against_criteria` | Quality assessment | Success validation |

## 🎨 CLI Commands

```bash
mco init [project-name]     # Create new MCO project
mco validate [config-dir]   # Validate SNLP files  
mco serve [config-dir]      # Start MCP server
mco templates              # List available templates
```

## 🤝 Contributing

We welcome contributions! MCO is designed to become the standard for agent orchestration.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🚀 Join the Revolution

**MCO Protocol is live and ready to transform how you build autonomous agents.**

- 📦 **Install**: `npm install -g @paradiselabs/mco-protocol`
- 🎮 **Demo**: [Interactive Gradio Space](https://huggingface.co/spaces/paradiselabs/mco-protocol-demo)
- 💬 **Discord**: [Join our community](https://discord.gg/uQ69vc4Agc)
- 🐦 **Twitter**: [@paradiselabs_ai](https://twitter.com/paradiselabs_ai)

---

<div align="center">

**🌟 Star this repository if MCO helps you build better agents! 🌟**

*Made with ❤️ by [Paradise Labs](https://paradiselabs.co)*

</div>
