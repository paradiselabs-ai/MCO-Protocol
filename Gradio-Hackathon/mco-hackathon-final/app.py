#!/usr/bin/env python3
"""
MCO Hackathon Final Submission - Main Entry Point

This script integrates all components of the MCO Hackathon project:
1. Real Modal API integration for AutoGPT-like agent
2. Real MCO MCP server for orchestration
3. Single-page Gradio UI with agent thinking and MCO logs
4. Visual SNLP generator with value/NLP editing toggle

Author: Manus AI
Date: June 10, 2025
"""

import os
import sys
import json
import subprocess
import tempfile
from pathlib import Path

# Set up environment
os.environ["MCO_CONFIG_DIR"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mco-config")

# Import components
from modal_implementation import app as modal_app
from gradio_ui import create_ui
from snlp_generator import SNLPGenerator

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
    generator = SNLPGenerator()
    
    # Check if any SNLP files exist
    if not any(os.path.exists(os.path.join(os.environ["MCO_CONFIG_DIR"], file)) 
               for file in ["mco.core", "mco.sc", "mco.features", "mco.styles"]):
        print("Creating sample SNLP files...")
        generator.generate_sample_files("General", "Python")
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

def validate_environment():
    """Validate the environment for running the application"""
    print("Validating environment...")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("Warning: Python 3.8+ recommended")
    
    # Check required packages
    required_packages = ["gradio", "modal", "anthropic", "requests", "beautifulsoup4"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} installed")
        except ImportError:
            missing_packages.append(package)
            print(f"✗ {package} missing")
    
    if missing_packages:
        print("\nInstalling missing packages...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install"] + missing_packages,
            check=True
        )
        print("Missing packages installed")
    
    # Check Node.js
    try:
        node_version = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        print(f"Node.js version: {node_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: Node.js not found, required for MCO MCP server")
    
    # Check npm
    try:
        npm_version = subprocess.run(
            ["npm", "--version"],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        print(f"npm version: {npm_version}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: npm not found, required for MCO MCP server")
    
    # Check environment variables
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Warning: ANTHROPIC_API_KEY environment variable not set")
    
    print("Environment validation complete")

def main():
    """Main entry point"""
    print("Starting MCO Hackathon project...")
    
    # Validate environment
    validate_environment()
    
    # Set up MCO server
    setup_mco_server()
    
    # Set up Modal
    setup_modal()
    
    # Create and launch Gradio UI
    print("Launching Gradio UI...")
    app = create_ui()
    app.launch()

if __name__ == "__main__":
    main()
