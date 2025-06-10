"""
Main entry point for the MCO Hackathon project.

This file integrates the Modal agent implementation with the Gradio UI
to provide a complete end-to-end demonstration of MCO orchestration.
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path

# Ensure the MCO config directory exists
MCO_CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mco-config")
os.makedirs(MCO_CONFIG_DIR, exist_ok=True)

# Import Gradio UI
from gradio_ui import create_ui

# Check if running in Hugging Face Spaces
IS_HF_SPACE = os.environ.get("SPACE_ID") is not None

def setup_mco_server():
    """Set up the MCO MCP server"""
    print("Setting up MCO MCP server...")
    
    # Check if mco-mcp-server.js exists
    server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mco-mcp-server.js")
    if not os.path.exists(server_path):
        print(f"Warning: MCO MCP server not found at {server_path}")
        print("Downloading from npm package...")
        
        # Install MCO package if not already installed
        try:
            subprocess.run(
                ["npm", "list", "@paradiselabs/mco-protocol"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except subprocess.CalledProcessError:
            print("Installing @paradiselabs/mco-protocol...")
            subprocess.run(
                ["npm", "install", "@paradiselabs/mco-protocol"],
                check=True
            )
        
        # Copy server file from node_modules
        import shutil
        node_modules_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "node_modules")
        mco_server_path = os.path.join(node_modules_path, "@paradiselabs/mco-protocol/bin/mco-mcp-server.js")
        
        if os.path.exists(mco_server_path):
            shutil.copy(mco_server_path, server_path)
            print(f"Copied MCO MCP server to {server_path}")
        else:
            print(f"Error: Could not find MCO MCP server in node_modules")
    
    # Create sample SNLP files if they don't exist
    create_sample_snlp_files()
    
    print("MCO MCP server setup complete")

def create_sample_snlp_files():
    """Create sample SNLP files if they don't exist"""
    core_file = os.path.join(MCO_CONFIG_DIR, "mco.core")
    sc_file = os.path.join(MCO_CONFIG_DIR, "mco.sc")
    features_file = os.path.join(MCO_CONFIG_DIR, "mco.features")
    styles_file = os.path.join(MCO_CONFIG_DIR, "mco.styles")
    
    # Only create if none of the files exist
    if not (os.path.exists(core_file) or os.path.exists(sc_file) or 
            os.path.exists(features_file) or os.path.exists(styles_file)):
        print("Creating sample SNLP files...")
        
        # Create mco.core
        with open(core_file, "w") as f:
            f.write("""// MCO Core Configuration

@workflow "Code Review Assistant"
>This is an AI assistant that performs thorough code reviews with a focus on best practices.
>The workflow follows a structured progression to ensure comprehensive and reliable code reviews.

@description "Multi-step code review workflow with progressive revelation"
>This workflow demonstrates MCO's progressive revelation capability - core requirements stay persistent while features and styles are strategically injected at optimal moments.
>The agent should maintain focus on the current step while building upon previous work.

@version "1.0.0"

// Data Section - Persistent state throughout workflow
@data
  language: "Python"
  review_type: "General"
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
""")
        
        # Create mco.sc
        with open(sc_file, "w") as f:
            f.write("""// MCO Success Criteria

@goal "Create a comprehensive code review system"
>The goal is to build a reliable, autonomous code review system that can analyze code,
>identify issues, suggest improvements, and generate test cases.

@success_criteria
  - "Correctly identify syntax errors and bugs in code"
  - "Provide specific, actionable suggestions for code improvement"
  - "Generate relevant test cases that cover edge cases"
  - "Maintain consistent focus on best practices"
  - "Produce a well-organized, comprehensive review report"
  - "Complete the entire workflow without human intervention"
>The success criteria define what a successful code review should accomplish.
>Each criterion should be measurable and verifiable.

@target_audience "Software developers and code reviewers"
>The primary users are software developers who want automated code reviews for their projects.
>They need detailed, actionable feedback to improve their code quality and reliability.

@developer_vision "Reliable, consistent code reviews that improve code quality"
>The vision is to create a system that provides the same level of detail and insight as a human code reviewer,
>but with greater consistency and without the limitations of human reviewers (fatigue, bias, etc.).
""")
        
        # Create mco.features
        with open(features_file, "w") as f:
            f.write("""// MCO Features

@feature "Static Analysis"
>Perform static analysis of code to identify syntax errors, potential bugs, and code smells.
>Use language-specific rules and best practices to evaluate code quality.

@feature "Security Scanning"
>Scan code for security vulnerabilities such as injection flaws, authentication issues, and data exposure risks.
>Prioritize findings based on severity and potential impact.

@feature "Performance Optimization"
>Identify performance bottlenecks and inefficient algorithms or data structures.
>Suggest optimizations that improve execution speed and resource usage.

@feature "Code Style Enforcement"
>Check adherence to coding standards and style guidelines.
>Ensure consistent formatting, naming conventions, and documentation.

@feature "Test Coverage Analysis"
>Evaluate the completeness of test coverage for the codebase.
>Identify untested code paths and suggest additional test cases.

@feature "Refactoring Suggestions"
>Recommend code refactoring to improve maintainability, readability, and extensibility.
>Provide specific examples of refactored code.
""")
        
        # Create mco.styles
        with open(styles_file, "w") as f:
            f.write("""// MCO Styles

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
""")
        
        print("Sample SNLP files created")

def setup_modal():
    """Set up Modal for deployment"""
    if IS_HF_SPACE:
        print("Running in Hugging Face Space, skipping Modal setup")
        return
    
    try:
        import modal
        
        # Check if Modal is set up
        try:
            modal.Image.debian_slim()
            print("Modal is set up and ready to use")
        except Exception as e:
            print(f"Modal setup required: {str(e)}")
            print("Please run 'modal token new' to set up Modal")
    except ImportError:
        print("Modal not installed, installing...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "modal"],
            check=True
        )
        print("Modal installed, please restart the application")

def main():
    """Main entry point"""
    print("Starting MCO Hackathon project...")
    
    # Set up MCO server
    setup_mco_server()
    
    # Set up Modal
    setup_modal()
    
    # Create and launch Gradio UI
    app = create_ui()
    app.launch()

if __name__ == "__main__":
    main()
