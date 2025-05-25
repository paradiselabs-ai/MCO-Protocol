"""
Configuration Manager for MCO Server

This module provides functionality for loading and managing MCO configuration files
while preserving the original Percertain DSL structure and progressive revelation approach.
"""

from typing import Dict, Any, Optional, List
import os
import json
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manages MCO configuration files and provides access to configuration data.
    Preserves the exact Percertain DSL structure and progressive revelation approach.
    """
    
    def __init__(self):
        """Initialize the configuration manager with all file types."""
        self.core_config = {}  # mco.core
        self.success_criteria = {}  # mco.sc
        self.features = {}  # mco.features
        self.styles = {}  # mco.styles
        self.config_dir = None
    
    def load_from_directory(self, config_dir: str) -> None:
        """
        Load configuration from a directory containing MCO files.
        Preserves the exact file structure and parsing approach.
        """
        if not os.path.isdir(config_dir):
            raise ValueError(f"Configuration directory does not exist: {config_dir}")
        
        self.config_dir = config_dir
        
        # Load core configuration files (persistent memory)
        self._load_core_config(os.path.join(config_dir, "mco.core"))
        self._load_success_criteria(os.path.join(config_dir, "mco.sc"))
        
        # Load optional configuration files (injected at strategic points)
        features_path = os.path.join(config_dir, "mco.features")
        if os.path.exists(features_path):
            self._load_features(features_path)
        
        styles_path = os.path.join(config_dir, "mco.styles")
        if os.path.exists(styles_path):
            self._load_styles(styles_path)
        
        logger.info(f"Loaded configuration from {config_dir}")
    
    def get_core_config(self) -> Dict[str, Any]:
        """
        Get the core configuration.
        
        Returns:
            Core configuration dictionary
        """
        return self.core_config
    
    def get_success_criteria(self) -> Dict[str, Any]:
        """
        Get the success criteria configuration.
        
        Returns:
            Success criteria dictionary
        """
        return self.success_criteria
    
    def get_features(self) -> Dict[str, Any]:
        """
        Get the features configuration.
        
        Returns:
            Features dictionary
        """
        return self.features
    
    def get_styles(self) -> Dict[str, Any]:
        """
        Get the styles configuration.
        
        Returns:
            Styles dictionary
        """
        return self.styles
    
    def get_workflow_steps(self) -> List[Dict[str, Any]]:
        """
        Get the workflow steps from the core configuration.
        
        Returns:
            List of workflow step dictionaries
        """
        if "workflow_steps" not in self.core_config:
            return []
        
        steps = []
        for step_id, step_data in self.core_config["workflow_steps"].items():
            step = {
                "id": step_id,
                **step_data
            }
            steps.append(step)
        
        return steps
    
    def get_target_audience(self) -> str:
        """
        Get the target audience from the success criteria.
        
        Returns:
            Target audience string
        """
        return self.success_criteria.get("target_audience", "")
    
    def get_developer_vision(self) -> str:
        """
        Get the developer vision from the success criteria.
        
        Returns:
            Developer vision string
        """
        return self.success_criteria.get("developer_vision", "")
    
    def get_goal(self) -> str:
        """
        Get the goal from the success criteria.
        
        Returns:
            Goal string
        """
        return self.success_criteria.get("goal", "")
    
    def get_success_criterion(self, criterion_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific success criterion by ID.
        
        Args:
            criterion_id: ID of the success criterion
            
        Returns:
            Success criterion dictionary or None if not found
        """
        if "success_criteria" not in self.success_criteria:
            return None
        
        for criterion in self.success_criteria["success_criteria"]:
            if criterion.get("id") == criterion_id:
                return criterion
        
        return None
    
    def _load_core_config(self, file_path: str) -> None:
        """
        Load core configuration from a file.
        
        Args:
            file_path: Path to the mco.core file
        """
        if not os.path.exists(file_path):
            raise ValueError(f"Core configuration file not found: {file_path}")
        
        try:
            with open(file_path, "r") as f:
                content = f.read()
            
            # Parse MCO format
            self.core_config = self._parse_mco_format(content)
            logger.debug(f"Loaded core configuration from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading core configuration: {e}")
            raise
    
    def _load_success_criteria(self, file_path: str) -> None:
        """
        Load success criteria from a file.
        
        Args:
            file_path: Path to the mco.sc file
        """
        if not os.path.exists(file_path):
            raise ValueError(f"Success criteria file not found: {file_path}")
        
        try:
            with open(file_path, "r") as f:
                content = f.read()
            
            # Parse MCO format
            self.success_criteria = self._parse_mco_format(content)
            logger.debug(f"Loaded success criteria from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading success criteria: {e}")
            raise
    
    def _load_features(self, file_path: str) -> None:
        """
        Load features from a file.
        
        Args:
            file_path: Path to the mco.features file
        """
        if not os.path.exists(file_path):
            return
        
        try:
            with open(file_path, "r") as f:
                content = f.read()
            
            # Parse MCO format
            self.features = self._parse_mco_format(content)
            logger.debug(f"Loaded features from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading features: {e}")
            raise
    
    def _load_styles(self, file_path: str) -> None:
        """
        Load styles from a file.
        
        Args:
            file_path: Path to the mco.styles file
        """
        if not os.path.exists(file_path):
            return
        
        try:
            with open(file_path, "r") as f:
                content = f.read()
            
            # Parse MCO format
            self.styles = self._parse_mco_format(content)
            logger.debug(f"Loaded styles from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading styles: {e}")
            raise
    
    def _parse_mco_format(self, content: str) -> Dict[str, Any]:
        """
        Parse MCO format content into a dictionary.
        Preserves the exact syntax parsing including comments and NLP sections.
        """
        result = {}
        current_section = None
        section_content = []
        nlp_content = []
        in_nlp_block = False
        
        for line in content.split("\n"):
            line_stripped = line.strip()
            
            # Skip empty lines and comments (but preserve them in the parsed structure)
            if not line_stripped or line_stripped.startswith("//"):
                if current_section:
                    section_content.append(line)
                continue
            
            # Check for NLP blocks
            if line_stripped.startswith("> "):
                in_nlp_block = True
                nlp_text = line_stripped[2:].strip('"')
                nlp_content.append(nlp_text)
                continue
            
            # Check for section start
            if line_stripped.startswith("@"):
                # Save previous section if exists
                if current_section:
                    section_data = self._parse_section_content(section_content)
                    
                    # Add NLP content if exists
                    if nlp_content:
                        section_data["_nlp"] = nlp_content
                    
                    result[current_section] = section_data
                    nlp_content = []
                
                # Start new section
                section_parts = line_stripped[1:].split(":", 1)
                current_section = section_parts[0].strip()
                section_content = [line]
                in_nlp_block = False
                continue
            
            # Add line to current section
            if current_section:
                section_content.append(line)
        
        # Save last section
        if current_section:
            section_data = self._parse_section_content(section_content)
            
            # Add NLP content if exists
            if nlp_content:
                section_data["_nlp"] = nlp_content
            
            result[current_section] = section_data
        
        return result
    
    def _parse_section_content(self, content: List[str]) -> Any:
        """
        Parse section content based on format.
        Handles structured data, lists, and free text formats.
        
        Args:
            content: List of content lines
            
        Returns:
            Parsed content
        """
        # Join all non-comment lines
        joined_content = ""
        for line in content:
            line_stripped = line.strip()
            if not line_stripped.startswith("//"):
                joined_content += line + "\n"
        
        # Try to parse as JSON if it looks like JSON
        if (joined_content.strip().startswith("{") and joined_content.strip().endswith("}")) or \
           (joined_content.strip().startswith("[") and joined_content.strip().endswith("]")):
            try:
                # Try to parse as JSON
                return json.loads(joined_content)
            except json.JSONDecodeError:
                pass
        
        # If not JSON, parse based on content structure
        result = {}
        current_key = None
        current_value = []
        list_items = []
        
        # Check if it's a simple list of items
        is_list = True
        for line in content:
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith("//"):
                continue
            if line_stripped.startswith("-"):
                list_items.append(line_stripped[1:].strip())
            else:
                is_list = False
                break
        
        if is_list and list_items:
            return list_items
        
        # Otherwise parse as key-value pairs or structured data
        for line in content:
            line_stripped = line.strip()
            
            # Skip comments and empty lines
            if not line_stripped or line_stripped.startswith("//"):
                continue
            
            # Skip section declaration line
            if line_stripped.startswith("@"):
                continue
            
            # Check for key-value pair
            if ":" in line_stripped and not line_stripped.startswith("-"):
                # Save previous key-value pair if exists
                if current_key and current_value:
                    result[current_key] = "\n".join(current_value).strip()
                    current_value = []
                
                # Parse new key-value pair
                key, value = line_stripped.split(":", 1)
                current_key = key.strip()
                value_stripped = value.strip()
                
                # Check if value is a nested structure
                if value_stripped.startswith("{") or value_stripped.startswith("["):
                    try:
                        result[current_key] = json.loads(value_stripped)
                        current_key = None
                    except json.JSONDecodeError:
                        current_value.append(value_stripped)
                else:
                    current_value.append(value_stripped)
            
            # Handle list items
            elif line_stripped.startswith("-"):
                if "items" not in result:
                    result["items"] = []
                result["items"].append(line_stripped[1:].strip())
            
            # Add to current value if in a key-value pair
            elif current_key:
                current_value.append(line_stripped)
            
            # Add as raw text if not in a key-value pair
            else:
                if "text" not in result:
                    result["text"] = []
                result["text"].append(line_stripped)
        
        # Save last key-value pair if exists
        if current_key and current_value:
            result[current_key] = "\n".join(current_value).strip()
        
        # If result is empty or only has text, return the raw content
        if not result or (len(result) == 1 and "text" in result):
            # Join all non-comment, non-section lines
            raw_content = []
            for line in content:
                line_stripped = line.strip()
                if not line_stripped.startswith("//") and not line_stripped.startswith("@"):
                    raw_content.append(line)
            return "\n".join(raw_content).strip()
        
        return result
