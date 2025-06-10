"""
Modal Implementation for AutoGPT-like Agent with MCO Integration

This file implements a real AutoGPT-like agent using Modal that integrates with the MCO MCP server
for orchestration. The agent can perform code review tasks and generate MCO workflow files.
"""

import os
import json
import subprocess
import tempfile
import time
from pathlib import Path
import anthropic
import modal
import requests
from bs4 import BeautifulSoup

# Define the Modal app
app = modal.App("mco-autogpt-agent")

# Base image with required dependencies
image = modal.Image.debian_slim().pip_install(
    "anthropic",
    "requests",
    "python-dotenv",
    "beautifulsoup4",
    "numpy",
    "pandas",
    "matplotlib"
)

# Create a volume for persistent storage
volume = modal.Volume.from_name("mco-agent-volume", create_if_missing=True)

# Environment setup
env = {
    "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY", ""),
    "MCO_CONFIG_DIR": "/data/mco-config"
}

class MCPClient:
    """Client for interacting with MCO MCP server via subprocess"""
    
    def __init__(self, config_dir, orchestration_id=None):
        self.config_dir = config_dir
        self.orchestration_id = orchestration_id
        self.mco_server_process = None
        
    def _ensure_server_running(self):
        """Ensure the MCO MCP server is running"""
        if self.mco_server_process is None:
            # Start the MCO MCP server
            env = os.environ.copy()
            env["MCO_CONFIG_DIR"] = self.config_dir
            
            # Use MCP Inspector to start the server
            self.mco_server_process = subprocess.Popen(
                ["npx", "@modelcontextprotocol/inspector", "node", "mco-mcp-server.js"],
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to initialize
            time.sleep(2)
            
    def _call_tool(self, tool_name, params):
        """Call an MCO tool via MCP Inspector"""
        self._ensure_server_running()
        
        # Create temporary file for tool call
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as f:
            json.dump({
                "name": tool_name,
                "arguments": params
            }, f)
            tool_file = f.name
        
        # Call the tool using MCP Inspector
        result = subprocess.run(
            ["npx", "@modelcontextprotocol/inspector", "call-tool", "--tool-file", tool_file],
            capture_output=True,
            text=True
        )
        
        # Clean up temporary file
        os.unlink(tool_file)
        
        # Parse and return result
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"error": "Failed to parse tool result", "stdout": result.stdout, "stderr": result.stderr}
    
    def start_orchestration(self, config=None):
        """Start a new orchestration workflow"""
        config = config or {}
        result = self._call_tool("start_orchestration", {"config": config})
        
        if "orchestration_id" in result:
            self.orchestration_id = result["orchestration_id"]
            
        return result
    
    def get_next_directive(self):
        """Get the next directive from the orchestration"""
        if not self.orchestration_id:
            raise ValueError("No active orchestration")
            
        return self._call_tool("get_next_directive", {"orchestration_id": self.orchestration_id})
    
    def complete_step(self, step_id, result):
        """Complete a step in the orchestration"""
        if not self.orchestration_id:
            raise ValueError("No active orchestration")
            
        return self._call_tool("complete_step", {
            "orchestration_id": self.orchestration_id,
            "step_id": step_id,
            "result": result
        })
    
    def get_workflow_status(self):
        """Get the current status of the workflow"""
        if not self.orchestration_id:
            raise ValueError("No active orchestration")
            
        return self._call_tool("get_workflow_status", {"orchestration_id": self.orchestration_id})
    
    def get_persistent_context(self):
        """Get the persistent context for the workflow"""
        if not self.orchestration_id:
            raise ValueError("No active orchestration")
            
        return self._call_tool("get_persistent_context", {"orchestration_id": self.orchestration_id})
    
    def cleanup(self):
        """Clean up resources"""
        if self.mco_server_process:
            self.mco_server_process.terminate()
            self.mco_server_process = None

class AutoGPTAgent:
    """AutoGPT-like agent that can be orchestrated by MCO"""
    
    def __init__(self, task, config_dir, orchestration_id=None):
        self.task = task
        self.config_dir = config_dir
        self.mcp_client = MCPClient(config_dir, orchestration_id)
        self.memory = []
        self.thinking_log = []
        self.orchestration_log = []
        self.client = anthropic.Anthropic()
        
    def run(self):
        """Run the agent with MCO orchestration"""
        # Log the start of orchestration
        self.orchestration_log.append({
            "timestamp": time.time(),
            "event": "orchestration_start",
            "task": self.task
        })
        
        # If no orchestration ID, start new orchestration
        if not self.mcp_client.orchestration_id:
            config = {"task": self.task}
            start_result = self.mcp_client.start_orchestration(config)
            
            self.orchestration_log.append({
                "timestamp": time.time(),
                "event": "orchestration_created",
                "orchestration_id": self.mcp_client.orchestration_id
            })
        
        results = []
        
        # Main agent loop
        while True:
            # Get next directive from MCO
            directive = self.mcp_client.get_next_directive()
            
            self.orchestration_log.append({
                "timestamp": time.time(),
                "event": "directive_received",
                "directive_type": directive.get("type"),
                "step_id": directive.get("step_id")
            })
            
            if directive.get("type") == "complete":
                # Workflow is complete
                self.orchestration_log.append({
                    "timestamp": time.time(),
                    "event": "orchestration_complete"
                })
                break
            
            # Check for injected context
            if directive.get("injected_context"):
                self.orchestration_log.append({
                    "timestamp": time.time(),
                    "event": "context_injected",
                    "context_type": list(directive.get("injected_context", {}).keys())
                })
            
            # Process directive
            result = self._process_directive(directive)
            results.append(result)
            
            # Complete step
            complete_result = self.mcp_client.complete_step(directive["step_id"], result)
            
            self.orchestration_log.append({
                "timestamp": time.time(),
                "event": "step_completed",
                "step_id": directive["step_id"],
                "status": complete_result.get("status")
            })
        
        # Clean up
        self.mcp_client.cleanup()
        
        return {
            "results": results,
            "thinking_log": self.thinking_log,
            "orchestration_log": self.orchestration_log
        }
    
    def _process_directive(self, directive):
        """Process a directive from MCO"""
        # Extract information from directive
        instruction = directive["instruction"]
        context = directive["persistent_context"]
        injected = directive.get("injected_context", {})
        
        # Add to memory
        self.memory.append({
            "role": "system",
            "content": f"Directive: {instruction}\nContext: {json.dumps(context)}"
        })
        
        if injected:
            self.memory.append({
                "role": "system",
                "content": f"Additional context: {json.dumps(injected)}"
            })
        
        # Generate thinking process
        thinking = self._generate_thinking(instruction, context, injected)
        
        # Log thinking
        self.thinking_log.append({
            "timestamp": time.time(),
            "directive": instruction,
            "thinking": thinking
        })
        
        # Execute tools based on thinking
        tool_results = self._execute_tools(thinking)
        
        # Generate summary
        summary = self._generate_summary(instruction, thinking, tool_results)
        
        return {
            "thinking": thinking,
            "tool_results": tool_results,
            "summary": summary
        }
    
    def _generate_thinking(self, instruction, context, injected):
        """Generate thinking process using Claude"""
        # Prepare prompt for Claude
        prompt = f"""
        <task>{instruction}</task>
        
        <context>
        {json.dumps(context, indent=2)}
        </context>
        
        {"<injected>" + json.dumps(injected, indent=2) + "</injected>" if injected else ""}
        
        <memory>
        {self._format_memory()}
        </memory>
        
        <available_tools>
        - execute_code(code: str, language: str) -> Executes code and returns the result
        - search_web(query: str) -> Searches the web and returns results
        - read_file(path: str) -> Reads a file and returns its content
        - write_file(path: str, content: str) -> Writes content to a file
        - analyze_code(code: str, language: str) -> Analyzes code for issues
        </available_tools>
        
        <thinking>
        """
        
        # Call Claude API
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20240229",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
            stop_sequences=["</thinking>"]
        )
        
        return message.content[0].text
    
    def _execute_tools(self, thinking):
        """Extract and execute tools from thinking"""
        # Extract tool calls
        tool_calls = self._extract_tool_calls(thinking)
        
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            # Execute the appropriate tool
            if tool_name == "execute_code":
                result = self._execute_code(tool_args.get("code", ""), tool_args.get("language", "python"))
            elif tool_name == "search_web":
                result = self._search_web(tool_args.get("query", ""))
            elif tool_name == "read_file":
                result = self._read_file(tool_args.get("path", ""))
            elif tool_name == "write_file":
                result = self._write_file(tool_args.get("path", ""), tool_args.get("content", ""))
            elif tool_name == "analyze_code":
                result = self._analyze_code(tool_args.get("code", ""), tool_args.get("language", ""))
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            results.append({
                "tool": tool_name,
                "args": tool_args,
                "result": result
            })
            
            # Add to memory
            self.memory.append({
                "role": "function",
                "name": tool_name,
                "content": json.dumps(result)
            })
        
        return results
    
    def _generate_summary(self, instruction, thinking, tool_results):
        """Generate a summary of the results"""
        # Prepare prompt for Claude
        prompt = f"""
        <instruction>{instruction}</instruction>
        
        <thinking>
        {thinking}
        </thinking>
        
        <tool_results>
        {json.dumps(tool_results, indent=2)}
        </tool_results>
        
        Please provide a concise summary of the results and how they address the instruction.
        """
        
        # Call Claude API
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return message.content[0].text
    
    def _extract_tool_calls(self, thinking):
        """Extract tool calls from thinking text"""
        tool_calls = []
        
        # Simple regex-like extraction (in a real implementation, use proper parsing)
        lines = thinking.split("\n")
        for i, line in enumerate(lines):
            if "execute_code(" in line or "search_web(" in line or "read_file(" in line or "write_file(" in line or "analyze_code(" in line:
                # Extract tool name
                tool_name = line.split("(")[0].strip()
                
                # Find the closing parenthesis
                code_block = ""
                j = i
                while j < len(lines) and ")" not in lines[j]:
                    code_block += lines[j] + "\n"
                    j += 1
                
                if j < len(lines):
                    code_block += lines[j].split(")")[0]
                
                # Parse arguments
                args = {}
                if tool_name == "execute_code":
                    args = {"code": code_block, "language": "python"}
                elif tool_name == "search_web":
                    args = {"query": code_block.strip()}
                elif tool_name == "read_file":
                    args = {"path": code_block.strip()}
                elif tool_name == "write_file":
                    parts = code_block.split(",", 1)
                    if len(parts) == 2:
                        args = {"path": parts[0].strip(), "content": parts[1].strip()}
                elif tool_name == "analyze_code":
                    args = {"code": code_block, "language": "python"}
                
                tool_calls.append({
                    "name": tool_name,
                    "args": args
                })
        
        return tool_calls
    
    def _format_memory(self):
        """Format memory for inclusion in prompt"""
        formatted = ""
        for item in self.memory[-5:]:  # Only include the last 5 memory items
            if item["role"] == "system":
                formatted += f"System: {item['content']}\n\n"
            elif item["role"] == "function":
                formatted += f"Function {item['name']}: {item['content']}\n\n"
        return formatted
    
    # Tool implementations
    def _execute_code(self, code, language):
        """Execute code in a sandbox environment"""
        if language.lower() != "python":
            return {"error": f"Unsupported language: {language}"}
        
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute the code
            result = subprocess.run(
                ["python", temp_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Clean up
            os.unlink(temp_file)
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _search_web(self, query):
        """Search the web for information"""
        try:
            # Use a search API (simplified for demo)
            response = requests.get(
                "https://api.duckduckgo.com/",
                params={"q": query, "format": "json"}
            )
            
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def _read_file(self, path):
        """Read a file from the agent's workspace"""
        try:
            full_path = Path(self.config_dir) / path
            with open(full_path, 'r') as f:
                content = f.read()
            return {"content": content}
        except Exception as e:
            return {"error": str(e)}
    
    def _write_file(self, path, content):
        """Write content to a file in the agent's workspace"""
        try:
            full_path = Path(self.config_dir) / path
            # Ensure directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(full_path, 'w') as f:
                f.write(content)
            return {"success": True, "path": str(full_path)}
        except Exception as e:
            return {"error": str(e)}
    
    def _analyze_code(self, code, language):
        """Analyze code for issues"""
        # In a real implementation, use a code analysis tool
        # For demo, use Claude to analyze
        prompt = f"""
        <code language="{language}">
        {code}
        </code>
        
        Please analyze this code for:
        1. Bugs and errors
        2. Security issues
        3. Performance concerns
        4. Style and best practices
        
        Provide specific line numbers and detailed explanations.
        """
        
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20240229",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {"analysis": message.content[0].text}

class CodeReviewAgent(AutoGPTAgent):
    """Specialized agent for code review tasks"""
    
    def __init__(self, task, config_dir, orchestration_id=None):
        super().__init__(task, config_dir, orchestration_id)
    
    def review_code(self, code_files):
        """Review multiple code files"""
        results = {}
        
        for file_path, code in code_files.items():
            # Determine language
            language = self._detect_language(file_path)
            
            # Analyze code
            analysis = self._analyze_code(code, language)
            
            # Generate suggestions
            suggestions = self._suggest_improvements(code, analysis, language)
            
            # Create test cases
            test_cases = self._generate_test_cases(code, language)
            
            # Compile results
            results[file_path] = {
                "language": language,
                "analysis": analysis,
                "suggestions": suggestions,
                "test_cases": test_cases
            }
        
        return results
    
    def _detect_language(self, file_path):
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".java": "java",
            ".c": "c",
            ".cpp": "c++",
            ".cs": "c#",
            ".go": "go",
            ".rb": "ruby",
            ".php": "php",
            ".swift": "swift",
            ".kt": "kotlin",
            ".rs": "rust",
            ".html": "html",
            ".css": "css",
            ".sql": "sql"
        }
        
        return language_map.get(ext, "unknown")
    
    def _suggest_improvements(self, code, analysis, language):
        """Generate improvement suggestions"""
        prompt = f"""
        <code language="{language}">
        {code}
        </code>
        
        <analysis>
        {analysis.get('analysis', '')}
        </analysis>
        
        Please suggest specific improvements to address the issues identified in the analysis.
        Include code snippets showing the improved version.
        """
        
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20240229",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {"suggestions": message.content[0].text}
    
    def _generate_test_cases(self, code, language):
        """Generate test cases for the code"""
        prompt = f"""
        <code language="{language}">
        {code}
        </code>
        
        Please generate comprehensive test cases for this code.
        Include:
        1. Unit tests for individual functions/methods
        2. Edge case tests
        3. Integration tests if applicable
        
        Provide the test code in the same language as the original code.
        """
        
        message = self.client.messages.create(
            model="claude-3-5-sonnet-20240229",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {"test_cases": message.content[0].text}
    
    def generate_snlp_files(self, review_type, language_focus):
        """Generate MCO SNLP files for a code review workflow"""
        # Generate mco.core
        core_content = self._generate_core_file(review_type, language_focus)
        
        # Generate mco.sc
        sc_content = self._generate_sc_file(review_type, language_focus)
        
        # Generate mco.features
        features_content = self._generate_features_file(review_type, language_focus)
        
        # Generate mco.styles
        styles_content = self._generate_styles_file(review_type, language_focus)
        
        # Write files to config directory
        self._write_file("mco.core", core_content)
        self._write_file("mco.sc", sc_content)
        self._write_file("mco.features", features_content)
        self._write_file("mco.styles", styles_content)
        
        return {
            "mco.core": core_content,
            "mco.sc": sc_content,
            "mco.features": features_content,
            "mco.styles": styles_content
        }
    
    def _generate_core_file(self, review_type, language_focus):
        """Generate mco.core file content"""
        return f"""// MCO Core Configuration

@workflow "Code Review Assistant"
>This is an AI assistant that performs thorough code reviews for {language_focus} code with a focus on {review_type}.
>The workflow follows a structured progression to ensure comprehensive and reliable code reviews.

@description "Multi-step code review workflow with progressive revelation"
>This workflow demonstrates MCO's progressive revelation capability - core requirements stay persistent while features and styles are strategically injected at optimal moments.
>The agent should maintain focus on the current step while building upon previous work.

@version "1.0.0"

// Data Section - Persistent state throughout workflow
@data
  language: "{language_focus}"
  review_type: "{review_type}"
  code_files: []
  issues_found: {}
  suggestions: {}
  test_results: {}
>Focus on building reliable, autonomous code review workflows that complete successfully without human intervention.
>The agent should maintain context across all steps and build upon previous work iteratively.
>Use the data variables to track state and progress throughout the workflow.

// Agents Section - Workflow execution structure
@agents
  orchestrator:
    name: "MCO Orchestrator"
    description: "Manages workflow state and progressive revelation"
    model: "claude-3-5-sonnet"
    steps:
      - "Understand the code review requirements and scope"
      - "Analyze code structure and organization"
      - "Identify bugs, errors, and potential issues"
      - "Evaluate code quality and adherence to best practices"
      - "Generate improvement suggestions with examples"
      - "Create comprehensive review report with actionable recommendations"
"""
    
    def _generate_sc_file(self, review_type, language_focus):
        """Generate mco.sc file content"""
        return f"""// MCO Success Criteria

@goal "Create a comprehensive code review system for {language_focus} code"
>The goal is to build a reliable, autonomous code review system that can analyze {language_focus} code,
>identify issues, suggest improvements, and generate test cases with a focus on {review_type}.

@success_criteria
  - "Correctly identify syntax errors and bugs in {language_focus} code"
  - "Provide specific, actionable suggestions for code improvement"
  - "Generate relevant test cases that cover edge cases"
  - "Maintain consistent focus on {review_type} aspects"
  - "Produce a well-organized, comprehensive review report"
  - "Complete the entire workflow without human intervention"
>The success criteria define what a successful code review should accomplish.
>Each criterion should be measurable and verifiable.

@target_audience "Software developers and code reviewers"
>The primary users are software developers who want automated code reviews for their {language_focus} projects.
>They need detailed, actionable feedback to improve their code quality and reliability.

@developer_vision "Reliable, consistent code reviews that improve code quality"
>The vision is to create a system that provides the same level of detail and insight as a human code reviewer,
>but with greater consistency and without the limitations of human reviewers (fatigue, bias, etc.).
"""
    
    def _generate_features_file(self, review_type, language_focus):
        """Generate mco.features file content"""
        return f"""// MCO Features

@feature "Static Analysis"
>Perform static analysis of {language_focus} code to identify syntax errors, potential bugs, and code smells.
>Use language-specific rules and best practices to evaluate code quality.

@feature "Security Scanning"
>Scan code for security vulnerabilities such as injection flaws, authentication issues, and data exposure risks.
>Prioritize findings based on severity and potential impact.

@feature "Performance Optimization"
>Identify performance bottlenecks and inefficient algorithms or data structures.
>Suggest optimizations that improve execution speed and resource usage.

@feature "Code Style Enforcement"
>Check adherence to coding standards and style guidelines for {language_focus}.
>Ensure consistent formatting, naming conventions, and documentation.

@feature "Test Coverage Analysis"
>Evaluate the completeness of test coverage for the codebase.
>Identify untested code paths and suggest additional test cases.

@feature "Refactoring Suggestions"
>Recommend code refactoring to improve maintainability, readability, and extensibility.
>Provide specific examples of refactored code.
"""
    
    def _generate_styles_file(self, review_type, language_focus):
        """Generate mco.styles file content"""
        return f"""// MCO Styles

@style "Comprehensive"
>Provide detailed analysis covering all aspects of the code, including syntax, semantics, style, and architecture.
>Leave no stone unturned in the review process.

@style "Actionable"
>Focus on providing specific, actionable feedback that can be immediately implemented.
>Include code examples and clear instructions for addressing issues.

@style "Educational"
>Explain the reasoning behind each suggestion to help developers learn and improve.
>Reference relevant documentation, best practices, and design patterns.

@style "Prioritized"
>Organize findings by severity and impact to help developers focus on the most important issues first.
>Clearly distinguish between critical issues and minor suggestions.

@style "Balanced"
>Acknowledge both strengths and weaknesses in the code to provide a balanced perspective.
>Highlight well-implemented patterns and clever solutions alongside areas for improvement.

@style "Collaborative"
>Frame feedback in a collaborative, constructive manner rather than being overly critical.
>Use language that encourages improvement rather than assigning blame.
"""

# Modal functions
@app.function(
    image=image,
    volumes={"/data": volume},
    timeout=600,
    env=env
)
def run_agent(task, config_dir="/data/mco-config", orchestration_id=None):
    """Run the AutoGPT-like agent with MCO orchestration"""
    agent = AutoGPTAgent(task, config_dir, orchestration_id)
    return agent.run()

@app.function(
    image=image,
    volumes={"/data": volume},
    timeout=600,
    env=env
)
def run_code_review(code_files, review_type, language_focus, config_dir="/data/mco-config", orchestration_id=None):
    """Run a code review using the specialized agent"""
    agent = CodeReviewAgent(f"Review {language_focus} code with focus on {review_type}", config_dir, orchestration_id)
    
    # Generate SNLP files
    snlp_files = agent.generate_snlp_files(review_type, language_focus)
    
    # Run the agent with MCO orchestration
    results = agent.run()
    
    # Add code review results
    if code_files:
        review_results = agent.review_code(code_files)
        results["code_review"] = review_results
    
    return results

@app.function(
    image=image,
    volumes={"/data": volume},
    env=env
)
def generate_snlp_files(review_type, language_focus, config_dir="/data/mco-config"):
    """Generate SNLP files for a code review workflow"""
    agent = CodeReviewAgent(f"Generate SNLP files for {language_focus} code review", config_dir)
    return agent.generate_snlp_files(review_type, language_focus)

@app.function(
    image=image,
    volumes={"/data": volume},
    env=env
)
def execute_code(code, language="python"):
    """Execute code in a sandbox environment"""
    agent = AutoGPTAgent("Execute code", "/data/mco-config")
    return agent._execute_code(code, language)

@app.function(
    image=image,
    env=env
)
def search_web(query):
    """Search the web for information"""
    agent = AutoGPTAgent("Search web", "/data/mco-config")
    return agent._search_web(query)

# Web endpoint
@app.endpoint(method="POST")
def agent_endpoint(task_description, review_type=None, language_focus=None, code_files=None):
    """Web endpoint for running the agent"""
    if review_type and language_focus:
        return run_code_review(code_files, review_type, language_focus)
    else:
        return run_agent(task_description)

if __name__ == "__main__":
    # For local testing
    print("Running agent locally...")
    result = run_agent("Create a simple code review workflow for Python")
    print(json.dumps(result, indent=2))
