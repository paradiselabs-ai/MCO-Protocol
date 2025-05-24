"""
Configuration Manager for MCO Server

This module provides functionality for loading and managing MCO configuration files.
"""

from typing import Dict, Any, Optional, List
import os
import json
import logging

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Manages MCO configuration files and provides access to configuration data.
    """
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.app_config = {}
        self.success_criteria = {}
        self.features = {}
        self.styles = {}
        self.config_dir = None
    
    def load_from_directory(self, config_dir: str) -> None:
        """
        Load configuration from a directory containing MCO files.
        
        Args:
            config_dir: Directory containing MCO configuration files
        """
        if not os.path.isdir(config_dir):
            raise ValueError(f"Configuration directory does not exist: {config_dir}")
        
        self.config_dir = config_dir
        
        # Load core configuration files
        self._load_app_config(os.path.join(config_dir, "mco.app"))
        self._load_success_criteria(os.path.join(config_dir, "mco.sc"))
        
        # Load optional configuration files
        features_path = os.path.join(config_dir, "mco.features")
        if os.path.exists(features_path):
            self._load_features(features_path)
        
        styles_path = os.path.join(config_dir, "mco.styles")
        if os.path.exists(styles_path):
            self._load_styles(styles_path)
        
        logger.info(f"Loaded configuration from {config_dir}")
    
    def get_app_config(self) -> Dict[str, Any]:
        """
        Get the application configuration.
        
        Returns:
            Application configuration dictionary
        """
        return self.app_config
    
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
        Get the workflow steps from the application configuration.
        
        Returns:
            List of workflow step dictionaries
        """
        if "workflow" not in self.app_config:
            return []
        
        if "steps" not in self.app_config["workflow"]:
            return []
        
        return self.app_config["workflow"]["steps"]
    
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
    
    def _load_app_config(self, file_path: str) -> None:
        """
        Load application configuration from a file.
        
        Args:
            file_path: Path to the mco.app file
        """
        if not os.path.exists(file_path):
            raise ValueError(f"Application configuration file not found: {file_path}")
        
        try:
            with open(file_path, "r") as f:
                content = f.read()
            
            # Parse MCO format
            self.app_config = self._parse_mco_format(content)
            logger.debug(f"Loaded application configuration from {file_path}")
            
        except Exception as e:
            logger.error(f"Error loading application configuration: {e}")
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
        
        Args:
            content: MCO format content
            
        Returns:
            Parsed dictionary
        """
        result = {}
        current_section = None
        section_content = []
        
        for line in content.split("\n"):
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith("#"):
                continue
            
            # Check for section start
            if line.startswith("@"):
                # Save previous section if exists
                if current_section:
                    result[current_section] = self._parse_section_content(section_content)
                
                # Start new section
                current_section = line[1:].split(":")[0].strip()
                section_content = []
                continue
            
            # Add line to current section
            if current_section:
                section_content.append(line)
        
        # Save last section
        if current_section:
            result[current_section] = self._parse_section_content(section_content)
        
        return result
    
    def _parse_section_content(self, content: List[str]) -> Any:
        """
        Parse section content based on format.
        
        Args:
            content: List of content lines
            
        Returns:
            Parsed content
        """
        # Join lines and try to parse as JSON
        joined_content = " ".join(content)
        
        try:
            # Try to parse as JSON
            return json.loads(joined_content)
        except json.JSONDecodeError:
            # If not valid JSON, parse as key-value pairs
            result = {}
            
            for line in content:
                if ":" in line:
                    key, value = line.split(":", 1)
                    result[key.strip()] = value.strip()
                else:
                    # Add as list item if no key-value format
                    if "items" not in result:
                        result["items"] = []
                    result["items"].append(line)
            
            return result
