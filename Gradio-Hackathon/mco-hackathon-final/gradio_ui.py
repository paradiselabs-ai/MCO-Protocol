"""
Gradio UI for AutoGPT-like Agent with MCO Integration

This file implements a single-page Gradio UI that shows:
1. Claude's thinking process as it's orchestrated by MCO
2. MCO orchestration logs
3. Visual SNLP generator with value/NLP editing toggle
"""

import os
import json
import time
import gradio as gr
import modal
import requests
from pathlib import Path

# Import the Modal app
try:
    from modal_implementation import app as modal_app
except ImportError:
    # For development without Modal
    modal_app = None

# Constants
DEFAULT_CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mco-config")
SNLP_FILES = ["mco.core", "mco.sc", "mco.features", "mco.styles"]

# Ensure config directory exists
os.makedirs(DEFAULT_CONFIG_DIR, exist_ok=True)

# Helper functions for SNLP parsing and generation
def parse_snlp_file(content):
    """Parse SNLP file content into sections"""
    sections = {}
    current_section = None
    current_content = []
    
    lines = content.split("\n")
    for line in lines:
        if line.startswith("@"):
            # Save previous section
            if current_section:
                sections[current_section] = "\n".join(current_content)
                current_content = []
            
            # Extract new section name
            parts = line.split(" ", 1)
            current_section = parts[0][1:]  # Remove the @ symbol
            
            # If there's content after the section name, add it
            if len(parts) > 1:
                current_content.append(parts[1])
        elif line.startswith(">"):
            # NLP content
            if current_section:
                current_content.append(line)
        else:
            # Regular content
            if current_section:
                current_content.append(line)
    
    # Save the last section
    if current_section:
        sections[current_section] = "\n".join(current_content)
    
    return sections

def generate_snlp_file(sections, file_type):
    """Generate SNLP file content from sections"""
    content = f"// MCO {file_type.capitalize()}\n\n"
    
    for section, section_content in sections.items():
        content += f"@{section}\n"
        
        # Split content into lines
        lines = section_content.split("\n")
        for line in lines:
            if line.startswith(">"):
                # NLP content
                content += f"{line}\n"
            else:
                # Regular content
                content += f"{line}\n"
        
        content += "\n"
    
    return content

def extract_values_and_nlp(content):
    """Extract values and NLP sections for the simplified editor"""
    values = {}
    nlp = {}
    
    sections = parse_snlp_file(content)
    for section, section_content in sections.items():
        # Extract NLP content
        nlp_content = []
        value_content = []
        
        lines = section_content.split("\n")
        for line in lines:
            if line.startswith(">"):
                nlp_content.append(line[1:].strip())  # Remove the > prefix
            else:
                value_content.append(line)
        
        if nlp_content:
            nlp[section] = "\n".join(nlp_content)
        
        if value_content:
            values[section] = "\n".join(value_content)
    
    return values, nlp

def update_values_and_nlp(content, values, nlp):
    """Update SNLP file with new values and NLP content"""
    sections = parse_snlp_file(content)
    updated_sections = {}
    
    for section, section_content in sections.items():
        updated_content = []
        
        # Add values
        if section in values:
            updated_content.append(values[section])
        
        # Add NLP
        if section in nlp:
            nlp_lines = nlp[section].split("\n")
            for line in nlp_lines:
                updated_content.append(f">{line}")
        
        updated_sections[section] = "\n".join(updated_content)
    
    # Generate updated file
    file_type = "core"
    if "success_criteria" in sections:
        file_type = "sc"
    elif "feature" in content:
        file_type = "features"
    elif "style" in content:
        file_type = "styles"
    
    return generate_snlp_file(updated_sections, file_type)

# Modal integration functions
def run_agent_with_modal(task, review_type=None, language_focus=None, code_files=None):
    """Run the agent using Modal"""
    if modal_app:
        if review_type and language_focus:
            return modal_app.run_code_review.remote(code_files, review_type, language_focus)
        else:
            return modal_app.run_agent.remote(task)
    else:
        # Simulated response for development without Modal
        return {
            "results": [
                {
                    "thinking": "I need to analyze the requirements and create a plan...",
                    "tool_results": [],
                    "summary": "Created initial plan for code review"
                }
            ],
            "thinking_log": [
                {
                    "timestamp": time.time(),
                    "directive": "Understand the code review requirements",
                    "thinking": "I need to analyze the requirements and create a plan..."
                }
            ],
            "orchestration_log": [
                {
                    "timestamp": time.time(),
                    "event": "orchestration_start",
                    "task": task
                },
                {
                    "timestamp": time.time(),
                    "event": "directive_received",
                    "directive_type": "execute",
                    "step_id": "step_1"
                }
            ]
        }

def generate_snlp_with_modal(review_type, language_focus):
    """Generate SNLP files using Modal"""
    if modal_app:
        return modal_app.generate_snlp_files.remote(review_type, language_focus)
    else:
        # Simulated response for development without Modal
        return {
            "mco.core": "// MCO Core Configuration\n\n@workflow \"Code Review Assistant\"\n>This is an AI assistant that performs code reviews...",
            "mco.sc": "// MCO Success Criteria\n\n@goal \"Create a comprehensive code review system\"\n>The goal is to build a reliable...",
            "mco.features": "// MCO Features\n\n@feature \"Static Analysis\"\n>Perform static analysis of code...",
            "mco.styles": "// MCO Styles\n\n@style \"Comprehensive\"\n>Provide detailed analysis covering all aspects..."
        }

# Gradio UI implementation
def create_ui():
    """Create the Gradio UI"""
    with gr.Blocks(theme=gr.themes.Soft(), title="MCO Protocol - AutoGPT Agent") as app:
        gr.Markdown("""
        # MCO Protocol - AutoGPT Agent with Real Orchestration
        
        This demo shows a real AutoGPT-like agent being orchestrated by the MCO MCP server.
        The agent can perform code reviews and generate MCO workflow files.
        """)
        
        # Main tabs
        with gr.Tabs() as tabs:
            # Agent tab
            with gr.TabItem("Agent Demo"):
                with gr.Row():
                    with gr.Column(scale=2):
                        task_input = gr.Textbox(
                            label="Task Description",
                            placeholder="Describe the task for the agent...",
                            lines=2
                        )
                        
                        with gr.Row():
                            review_type = gr.Dropdown(
                                label="Review Type",
                                choices=["Security", "Performance", "Style", "Maintainability", "General"],
                                value="General"
                            )
                            language_focus = gr.Dropdown(
                                label="Language Focus",
                                choices=["Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust"],
                                value="Python"
                            )
                        
                        code_input = gr.Code(
                            label="Code to Review (Optional)",
                            language="python",
                            lines=10
                        )
                        
                        run_button = gr.Button("Run Agent", variant="primary")
                    
                    with gr.Column(scale=1):
                        status = gr.Markdown("Ready to run agent...")
            
                # Agent output area
                with gr.Row():
                    with gr.Column(scale=1):
                        thinking_output = gr.Markdown(
                            label="Agent Thinking Process",
                            value="Agent thinking will appear here..."
                        )
                    
                    with gr.Column(scale=1):
                        orchestration_log = gr.JSON(
                            label="MCO Orchestration Log",
                            value=[]
                        )
                
                # Results area
                results_output = gr.Markdown(
                    label="Agent Results",
                    value="Results will appear here..."
                )
            
            # SNLP Generator tab
            with gr.TabItem("SNLP Generator"):
                with gr.Row():
                    with gr.Column(scale=1):
                        gr.Markdown("### Generate SNLP Files")
                        
                        snlp_review_type = gr.Dropdown(
                            label="Review Type",
                            choices=["Security", "Performance", "Style", "Maintainability", "General"],
                            value="General"
                        )
                        
                        snlp_language_focus = gr.Dropdown(
                            label="Language Focus",
                            choices=["Python", "JavaScript", "TypeScript", "Java", "C++", "Go", "Rust"],
                            value="Python"
                        )
                        
                        generate_button = gr.Button("Generate SNLP Files", variant="primary")
                    
                    with gr.Column(scale=1):
                        edit_mode = gr.Radio(
                            label="Edit Mode",
                            choices=["Values Only", "Full Edit"],
                            value="Values Only"
                        )
                
                # SNLP file tabs
                with gr.Tabs() as snlp_tabs:
                    core_tab = gr.TabItem("mco.core")
                    sc_tab = gr.TabItem("mco.sc")
                    features_tab = gr.TabItem("mco.features")
                    styles_tab = gr.TabItem("mco.styles")
                
                # Content for each SNLP file tab
                with core_tab:
                    with gr.Row(visible=False) as core_values_row:
                        core_values = gr.JSON(label="Values", value={})
                        core_nlp = gr.JSON(label="NLP", value={})
                    
                    core_content = gr.Code(
                        label="mco.core Content",
                        language="markdown",
                        lines=20,
                        value="// MCO Core Configuration\n\n// Generate SNLP files to see content here..."
                    )
                
                with sc_tab:
                    with gr.Row(visible=False) as sc_values_row:
                        sc_values = gr.JSON(label="Values", value={})
                        sc_nlp = gr.JSON(label="NLP", value={})
                    
                    sc_content = gr.Code(
                        label="mco.sc Content",
                        language="markdown",
                        lines=20,
                        value="// MCO Success Criteria\n\n// Generate SNLP files to see content here..."
                    )
                
                with features_tab:
                    with gr.Row(visible=False) as features_values_row:
                        features_values = gr.JSON(label="Values", value={})
                        features_nlp = gr.JSON(label="NLP", value={})
                    
                    features_content = gr.Code(
                        label="mco.features Content",
                        language="markdown",
                        lines=20,
                        value="// MCO Features\n\n// Generate SNLP files to see content here..."
                    )
                
                with styles_tab:
                    with gr.Row(visible=False) as styles_values_row:
                        styles_values = gr.JSON(label="Values", value={})
                        styles_nlp = gr.JSON(label="NLP", value={})
                    
                    styles_content = gr.Code(
                        label="mco.styles Content",
                        language="markdown",
                        lines=20,
                        value="// MCO Styles\n\n// Generate SNLP files to see content here..."
                    )
                
                # Download buttons
                with gr.Row():
                    download_core = gr.Button("Download mco.core")
                    download_sc = gr.Button("Download mco.sc")
                    download_features = gr.Button("Download mco.features")
                    download_styles = gr.Button("Download mco.styles")
                
                # Download all button
                download_all = gr.Button("Download All Files", variant="primary")
            
            # About tab
            with gr.TabItem("About MCO"):
                gr.Markdown("""
                ## About MCO Protocol
                
                MCO (Model Configuration Orchestration) is the missing orchestration layer for agent frameworks.
                It provides a structured way to orchestrate AI agents using Syntactic Natural Language Programming (SNLP).
                
                ### Key Features
                
                - **Progressive Revelation**: Strategically reveal information to agents at the right time
                - **Structured Workflows**: Define clear steps and success criteria for agent tasks
                - **MCP Integration**: Works with any MCP-enabled framework with one line of config
                - **Visual Configuration**: Create SNLP files without learning syntax
                
                ### Getting Started
                
                1. Install the MCO package: `npm install @paradiselabs/mco-protocol`
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
                3. Create SNLP files using the generator below
                4. Run your agent with MCO orchestration
                
                ### Learn More
                
                - [GitHub Repository](https://github.com/paradiselabs/mco-protocol)
                - [Documentation](https://mco-protocol.readthedocs.io/)
                - [Discord Community](https://discord.gg/mco-protocol)
                """)
        
        # Event handlers
        def run_agent_handler(task, review_type, language_focus, code):
            """Handle agent run button click"""
            status_updates = []
            
            # Update status
            status_updates.append("Starting agent with MCO orchestration...")
            yield status_updates[-1], thinking_output, orchestration_log, results_output
            
            # Prepare code files
            code_files = None
            if code:
                code_files = {"input.py": code}
            
            # Run agent
            status_updates.append("Running agent with Modal API...")
            yield status_updates[-1], thinking_output, orchestration_log, results_output
            
            try:
                result = run_agent_with_modal(task, review_type, language_focus, code_files)
                
                # Update thinking output
                thinking_html = ""
                for entry in result.get("thinking_log", []):
                    thinking_html += f"## Step: {entry.get('directive', 'Unknown')}\n\n"
                    thinking_html += f"```\n{entry.get('thinking', '')}\n```\n\n"
                
                # Update orchestration log
                log_entries = result.get("orchestration_log", [])
                
                # Update results
                results_html = "# Agent Results\n\n"
                for i, res in enumerate(result.get("results", [])):
                    results_html += f"## Result {i+1}\n\n"
                    results_html += f"### Summary\n{res.get('summary', '')}\n\n"
                    
                    if "tool_results" in res:
                        results_html += "### Tool Results\n\n"
                        for tool_result in res.get("tool_results", []):
                            results_html += f"**{tool_result.get('tool', '')}**\n\n"
                            results_html += f"```\n{json.dumps(tool_result.get('result', {}), indent=2)}\n```\n\n"
                
                # Add code review results if available
                if "code_review" in result:
                    results_html += "## Code Review Results\n\n"
                    for file_path, review in result.get("code_review", {}).items():
                        results_html += f"### File: {file_path}\n\n"
                        results_html += f"**Language:** {review.get('language', 'unknown')}\n\n"
                        results_html += f"**Analysis:**\n{review.get('analysis', {}).get('analysis', '')}\n\n"
                        results_html += f"**Suggestions:**\n{review.get('suggestions', {}).get('suggestions', '')}\n\n"
                
                status_updates.append("Agent run completed successfully!")
                return status_updates[-1], thinking_html, log_entries, results_html
            
            except Exception as e:
                error_message = f"Error running agent: {str(e)}"
                return error_message, thinking_output, orchestration_log, f"# Error\n\n{error_message}"
        
        def generate_snlp_handler(review_type, language_focus):
            """Handle SNLP generation button click"""
            try:
                # Generate SNLP files
                snlp_files = generate_snlp_with_modal(review_type, language_focus)
                
                # Extract values and NLP for each file
                core_vals, core_nlps = extract_values_and_nlp(snlp_files["mco.core"])
                sc_vals, sc_nlps = extract_values_and_nlp(snlp_files["mco.sc"])
                features_vals, features_nlps = extract_values_and_nlp(snlp_files["mco.features"])
                styles_vals, styles_nlps = extract_values_and_nlp(snlp_files["mco.styles"])
                
                # Save files locally
                for file_name, content in snlp_files.items():
                    with open(os.path.join(DEFAULT_CONFIG_DIR, file_name), "w") as f:
                        f.write(content)
                
                return (
                    snlp_files["mco.core"],
                    snlp_files["mco.sc"],
                    snlp_files["mco.features"],
                    snlp_files["mco.styles"],
                    core_vals,
                    core_nlps,
                    sc_vals,
                    sc_nlps,
                    features_vals,
                    features_nlps,
                    styles_vals,
                    styles_nlps
                )
            
            except Exception as e:
                error_message = f"Error generating SNLP files: {str(e)}"
                return (
                    f"// Error\n\n{error_message}",
                    f"// Error\n\n{error_message}",
                    f"// Error\n\n{error_message}",
                    f"// Error\n\n{error_message}",
                    {},
                    {},
                    {},
                    {},
                    {},
                    {},
                    {},
                    {}
                )
        
        def update_edit_mode(mode):
            """Update edit mode visibility"""
            values_visible = mode == "Values Only"
            full_edit_visible = mode == "Full Edit"
            
            return (
                gr.update(visible=values_visible),
                gr.update(visible=values_visible),
                gr.update(visible=values_visible),
                gr.update(visible=values_visible),
                gr.update(visible=full_edit_visible),
                gr.update(visible=full_edit_visible),
                gr.update(visible=full_edit_visible),
                gr.update(visible=full_edit_visible)
            )
        
        def update_core_content(values, nlp):
            """Update core content from values and NLP"""
            try:
                with open(os.path.join(DEFAULT_CONFIG_DIR, "mco.core"), "r") as f:
                    content = f.read()
                
                updated_content = update_values_and_nlp(content, values, nlp)
                
                # Save updated content
                with open(os.path.join(DEFAULT_CONFIG_DIR, "mco.core"), "w") as f:
                    f.write(updated_content)
                
                return updated_content
            except Exception as e:
                return f"// Error updating content: {str(e)}"
        
        def update_sc_content(values, nlp):
            """Update sc content from values and NLP"""
            try:
                with open(os.path.join(DEFAULT_CONFIG_DIR, "mco.sc"), "r") as f:
                    content = f.read()
                
                updated_content = update_values_and_nlp(content, values, nlp)
                
                # Save updated content
                with open(os.path.join(DEFAULT_CONFIG_DIR, "mco.sc"), "w") as f:
                    f.write(updated_content)
                
                return updated_content
            except Exception as e:
                return f"// Error updating content: {str(e)}"
        
        def update_features_content(values, nlp):
            """Update features content from values and NLP"""
            try:
                with open(os.path.join(DEFAULT_CONFIG_DIR, "mco.features"), "r") as f:
                    content = f.read()
                
                updated_content = update_values_and_nlp(content, values, nlp)
                
                # Save updated content
                with open(os.path.join(DEFAULT_CONFIG_DIR, "mco.features"), "w") as f:
                    f.write(updated_content)
                
                return updated_content
            except Exception as e:
                return f"// Error updating content: {str(e)}"
        
        def update_styles_content(values, nlp):
            """Update styles content from values and NLP"""
            try:
                with open(os.path.join(DEFAULT_CONFIG_DIR, "mco.styles"), "r") as f:
                    content = f.read()
                
                updated_content = update_values_and_nlp(content, values, nlp)
                
                # Save updated content
                with open(os.path.join(DEFAULT_CONFIG_DIR, "mco.styles"), "w") as f:
                    f.write(updated_content)
                
                return updated_content
            except Exception as e:
                return f"// Error updating content: {str(e)}"
        
        def save_core_content(content):
            """Save core content to file"""
            try:
                with open(os.path.join(DEFAULT_CONFIG_DIR, "mco.core"), "w") as f:
                    f.write(content)
                
                # Update values and NLP
                values, nlp = extract_values_and_nlp(content)
                return values, nlp
            except Exception as e:
                return {}, {}
        
        def save_sc_content(content):
            """Save sc content to file"""
            try:
                with open(os.path.join(DEFAULT_CONFIG_DIR, "mco.sc"), "w") as f:
                    f.write(content)
                
                # Update values and NLP
                values, nlp = extract_values_and_nlp(content)
                return values, nlp
            except Exception as e:
                return {}, {}
        
        def save_features_content(content):
            """Save features content to file"""
            try:
                with open(os.path.join(DEFAULT_CONFIG_DIR, "mco.features"), "w") as f:
                    f.write(content)
                
                # Update values and NLP
                values, nlp = extract_values_and_nlp(content)
                return values, nlp
            except Exception as e:
                return {}, {}
        
        def save_styles_content(content):
            """Save styles content to file"""
            try:
                with open(os.path.join(DEFAULT_CONFIG_DIR, "mco.styles"), "w") as f:
                    f.write(content)
                
                # Update values and NLP
                values, nlp = extract_values_and_nlp(content)
                return values, nlp
            except Exception as e:
                return {}, {}
        
        # Connect event handlers
        run_button.click(
            fn=run_agent_handler,
            inputs=[task_input, review_type, language_focus, code_input],
            outputs=[status, thinking_output, orchestration_log, results_output]
        )
        
        generate_button.click(
            fn=generate_snlp_handler,
            inputs=[snlp_review_type, snlp_language_focus],
            outputs=[
                core_content,
                sc_content,
                features_content,
                styles_content,
                core_values,
                core_nlp,
                sc_values,
                sc_nlp,
                features_values,
                features_nlp,
                styles_values,
                styles_nlp
            ]
        )
        
        edit_mode.change(
            fn=update_edit_mode,
            inputs=[edit_mode],
            outputs=[
                core_values_row,
                sc_values_row,
                features_values_row,
                styles_values_row,
                core_content,
                sc_content,
                features_content,
                styles_content
            ]
        )
        
        # Connect value editors to content updates
        core_values.change(
            fn=update_core_content,
            inputs=[core_values, core_nlp],
            outputs=[core_content]
        )
        
        core_nlp.change(
            fn=update_core_content,
            inputs=[core_values, core_nlp],
            outputs=[core_content]
        )
        
        sc_values.change(
            fn=update_sc_content,
            inputs=[sc_values, sc_nlp],
            outputs=[sc_content]
        )
        
        sc_nlp.change(
            fn=update_sc_content,
            inputs=[sc_values, sc_nlp],
            outputs=[sc_content]
        )
        
        features_values.change(
            fn=update_features_content,
            inputs=[features_values, features_nlp],
            outputs=[features_content]
        )
        
        features_nlp.change(
            fn=update_features_content,
            inputs=[features_values, features_nlp],
            outputs=[features_content]
        )
        
        styles_values.change(
            fn=update_styles_content,
            inputs=[styles_values, styles_nlp],
            outputs=[styles_content]
        )
        
        styles_nlp.change(
            fn=update_styles_content,
            inputs=[styles_values, styles_nlp],
            outputs=[styles_content]
        )
        
        # Connect content editors to value updates
        core_content.change(
            fn=save_core_content,
            inputs=[core_content],
            outputs=[core_values, core_nlp]
        )
        
        sc_content.change(
            fn=save_sc_content,
            inputs=[sc_content],
            outputs=[sc_values, sc_nlp]
        )
        
        features_content.change(
            fn=save_features_content,
            inputs=[features_content],
            outputs=[features_values, features_nlp]
        )
        
        styles_content.change(
            fn=save_styles_content,
            inputs=[styles_content],
            outputs=[styles_values, styles_nlp]
        )
        
        # Connect download buttons
        download_core.click(
            fn=lambda: os.path.join(DEFAULT_CONFIG_DIR, "mco.core"),
            inputs=[],
            outputs=[gr.File(label="Download mco.core")]
        )
        
        download_sc.click(
            fn=lambda: os.path.join(DEFAULT_CONFIG_DIR, "mco.sc"),
            inputs=[],
            outputs=[gr.File(label="Download mco.sc")]
        )
        
        download_features.click(
            fn=lambda: os.path.join(DEFAULT_CONFIG_DIR, "mco.features"),
            inputs=[],
            outputs=[gr.File(label="Download mco.features")]
        )
        
        download_styles.click(
            fn=lambda: os.path.join(DEFAULT_CONFIG_DIR, "mco.styles"),
            inputs=[],
            outputs=[gr.File(label="Download mco.styles")]
        )
        
        # Connect download all button
        def create_zip():
            """Create a zip file of all SNLP files"""
            import zipfile
            import tempfile
            
            # Create a temporary zip file
            with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp:
                with zipfile.ZipFile(temp.name, "w") as zipf:
                    for file_name in SNLP_FILES:
                        file_path = os.path.join(DEFAULT_CONFIG_DIR, file_name)
                        if os.path.exists(file_path):
                            zipf.write(file_path, file_name)
                
                return temp.name
        
        download_all.click(
            fn=create_zip,
            inputs=[],
            outputs=[gr.File(label="Download All SNLP Files")]
        )
    
    return app

# Main function
def main():
    """Main function"""
    app = create_ui()
    app.launch()

if __name__ == "__main__":
    main()
