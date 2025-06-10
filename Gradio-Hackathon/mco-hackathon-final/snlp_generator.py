"""
Visual SNLP Generator Component for MCO Hackathon

This file implements the visual SNLP generator with value and NLP editing toggle
that allows users to easily create and edit MCO workflow files without learning syntax.
"""

import os
import json
import gradio as gr
from pathlib import Path
import zipfile
import tempfile

# Constants
DEFAULT_CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mco-config")
SNLP_FILES = ["mco.core", "mco.sc", "mco.features", "mco.styles"]

# Ensure config directory exists
os.makedirs(DEFAULT_CONFIG_DIR, exist_ok=True)

class SNLPGenerator:
    """Visual SNLP Generator with value and NLP editing toggle"""
    
    def __init__(self, config_dir=DEFAULT_CONFIG_DIR):
        """Initialize the SNLP Generator"""
        self.config_dir = config_dir
    
    def parse_snlp_file(self, content):
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
    
    def generate_snlp_file(self, sections, file_type):
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
    
    def extract_values_and_nlp(self, content):
        """Extract values and NLP sections for the simplified editor"""
        values = {}
        nlp = {}
        
        sections = self.parse_snlp_file(content)
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
    
    def update_values_and_nlp(self, content, values, nlp):
        """Update SNLP file with new values and NLP content"""
        sections = self.parse_snlp_file(content)
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
        
        return self.generate_snlp_file(updated_sections, file_type)
    
    def save_snlp_file(self, file_name, content):
        """Save SNLP file to disk"""
        file_path = os.path.join(self.config_dir, file_name)
        with open(file_path, "w") as f:
            f.write(content)
        return file_path
    
    def load_snlp_file(self, file_name):
        """Load SNLP file from disk"""
        file_path = os.path.join(self.config_dir, file_name)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return f.read()
        return None
    
    def create_zip_archive(self):
        """Create a zip archive of all SNLP files"""
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as temp:
            with zipfile.ZipFile(temp.name, "w") as zipf:
                for file_name in SNLP_FILES:
                    file_path = os.path.join(self.config_dir, file_name)
                    if os.path.exists(file_path):
                        zipf.write(file_path, file_name)
            
            return temp.name
    
    def generate_sample_files(self, review_type="General", language_focus="Python"):
        """Generate sample SNLP files"""
        # Generate mco.core
        core_content = f"""// MCO Core Configuration

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
  issues_found: {{}}
  suggestions: {{}}
  test_results: {{}}
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
        
        # Generate mco.sc
        sc_content = f"""// MCO Success Criteria

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
        
        # Generate mco.features
        features_content = f"""// MCO Features

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
        
        # Generate mco.styles
        styles_content = f"""// MCO Styles

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
        
        # Save files
        self.save_snlp_file("mco.core", core_content)
        self.save_snlp_file("mco.sc", sc_content)
        self.save_snlp_file("mco.features", features_content)
        self.save_snlp_file("mco.styles", styles_content)
        
        return {
            "mco.core": core_content,
            "mco.sc": sc_content,
            "mco.features": features_content,
            "mco.styles": styles_content
        }

def create_snlp_generator_ui():
    """Create the SNLP Generator UI component"""
    generator = SNLPGenerator()
    
    with gr.Blocks() as snlp_ui:
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Generate SNLP Files")
                
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
        
        # Event handlers
        def generate_snlp_handler(review_type, language_focus):
            """Handle SNLP generation button click"""
            try:
                # Generate SNLP files
                snlp_files = generator.generate_sample_files(review_type, language_focus)
                
                # Extract values and NLP for each file
                core_vals, core_nlps = generator.extract_values_and_nlp(snlp_files["mco.core"])
                sc_vals, sc_nlps = generator.extract_values_and_nlp(snlp_files["mco.sc"])
                features_vals, features_nlps = generator.extract_values_and_nlp(snlp_files["mco.features"])
                styles_vals, styles_nlps = generator.extract_values_and_nlp(snlp_files["mco.styles"])
                
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
                content = generator.load_snlp_file("mco.core")
                if not content:
                    return "// Error: mco.core file not found"
                
                updated_content = generator.update_values_and_nlp(content, values, nlp)
                
                # Save updated content
                generator.save_snlp_file("mco.core", updated_content)
                
                return updated_content
            except Exception as e:
                return f"// Error updating content: {str(e)}"
        
        def update_sc_content(values, nlp):
            """Update sc content from values and NLP"""
            try:
                content = generator.load_snlp_file("mco.sc")
                if not content:
                    return "// Error: mco.sc file not found"
                
                updated_content = generator.update_values_and_nlp(content, values, nlp)
                
                # Save updated content
                generator.save_snlp_file("mco.sc", updated_content)
                
                return updated_content
            except Exception as e:
                return f"// Error updating content: {str(e)}"
        
        def update_features_content(values, nlp):
            """Update features content from values and NLP"""
            try:
                content = generator.load_snlp_file("mco.features")
                if not content:
                    return "// Error: mco.features file not found"
                
                updated_content = generator.update_values_and_nlp(content, values, nlp)
                
                # Save updated content
                generator.save_snlp_file("mco.features", updated_content)
                
                return updated_content
            except Exception as e:
                return f"// Error updating content: {str(e)}"
        
        def update_styles_content(values, nlp):
            """Update styles content from values and NLP"""
            try:
                content = generator.load_snlp_file("mco.styles")
                if not content:
                    return "// Error: mco.styles file not found"
                
                updated_content = generator.update_values_and_nlp(content, values, nlp)
                
                # Save updated content
                generator.save_snlp_file("mco.styles", updated_content)
                
                return updated_content
            except Exception as e:
                return f"// Error updating content: {str(e)}"
        
        def save_core_content(content):
            """Save core content to file"""
            try:
                generator.save_snlp_file("mco.core", content)
                
                # Update values and NLP
                values, nlp = generator.extract_values_and_nlp(content)
                return values, nlp
            except Exception as e:
                return {}, {}
        
        def save_sc_content(content):
            """Save sc content to file"""
            try:
                generator.save_snlp_file("mco.sc", content)
                
                # Update values and NLP
                values, nlp = generator.extract_values_and_nlp(content)
                return values, nlp
            except Exception as e:
                return {}, {}
        
        def save_features_content(content):
            """Save features content to file"""
            try:
                generator.save_snlp_file("mco.features", content)
                
                # Update values and NLP
                values, nlp = generator.extract_values_and_nlp(content)
                return values, nlp
            except Exception as e:
                return {}, {}
        
        def save_styles_content(content):
            """Save styles content to file"""
            try:
                generator.save_snlp_file("mco.styles", content)
                
                # Update values and NLP
                values, nlp = generator.extract_values_and_nlp(content)
                return values, nlp
            except Exception as e:
                return {}, {}
        
        # Connect event handlers
        generate_button.click(
            fn=generate_snlp_handler,
            inputs=[review_type, language_focus],
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
            fn=lambda: os.path.join(generator.config_dir, "mco.core"),
            inputs=[],
            outputs=[gr.File(label="Download mco.core")]
        )
        
        download_sc.click(
            fn=lambda: os.path.join(generator.config_dir, "mco.sc"),
            inputs=[],
            outputs=[gr.File(label="Download mco.sc")]
        )
        
        download_features.click(
            fn=lambda: os.path.join(generator.config_dir, "mco.features"),
            inputs=[],
            outputs=[gr.File(label="Download mco.features")]
        )
        
        download_styles.click(
            fn=lambda: os.path.join(generator.config_dir, "mco.styles"),
            inputs=[],
            outputs=[gr.File(label="Download mco.styles")]
        )
        
        # Connect download all button
        download_all.click(
            fn=generator.create_zip_archive,
            inputs=[],
            outputs=[gr.File(label="Download All SNLP Files")]
        )
    
    return snlp_ui

if __name__ == "__main__":
    # For testing the SNLP generator component independently
    app = create_snlp_generator_ui()
    app.launch()
