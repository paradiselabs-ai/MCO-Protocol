"""
LM Studio Adapter for MCO Server

This module provides an adapter for the LM Studio Python SDK.
"""

from typing import Dict, Any, Optional
import logging
from ..adapters import BaseAdapter, register_adapter

logger = logging.getLogger(__name__)

@register_adapter("lmstudio")
class LMStudioAdapter(BaseAdapter):
    """
    Adapter for LM Studio Python SDK.
    """
    
    def __init__(self):
        """Initialize the LM Studio adapter."""
        super().__init__()
        self.model = None
        self.chat = None
        self.config = {}
    
    def initialize(self, config: Dict[str, Any]) -> None:
        """
        Initialize the adapter with configuration.
        
        Args:
            config: Configuration dictionary with LM Studio settings
        """
        try:
            import lmstudio
        except ImportError:
            raise ImportError(
                "LM Studio Python SDK not found. "
                "Please install it with: pip install lmstudio"
            )
        
        self.config = config
        
        # Initialize LM Studio model
        model_name = config.get("model_name", "qwen2.5-7b-instruct-1m")
        system_prompt = config.get("system_prompt", "You are a helpful assistant.")
        
        self.model = lmstudio.llm(model_name)
        self.chat = lmstudio.Chat(system_prompt)
        
        # Register callbacks if provided
        if "callbacks" in config:
            for callback_type, callback_func in config["callbacks"].items():
                self.model.register_callback(callback_type, callback_func)
        
        self.initialized = True
        logger.info(f"Initialized LM Studio adapter with model: {model_name}")
    
    def execute_directive(self, directive: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an orchestration directive using LM Studio.
        
        Args:
            directive: Directive dictionary
            
        Returns:
            Result dictionary
        """
        if not self.initialized:
            raise RuntimeError("LM Studio adapter not initialized")
        
        # Extract directive information
        instruction = directive.get("instruction", "")
        guidance = directive.get("guidance", "")
        
        # Combine instruction and guidance
        prompt = f"{instruction}\n\n{guidance}"
        
        try:
            # Generate response using LM Studio
            response = self.model.generate(prompt)
            
            # Create result dictionary
            result = {
                "output": response,
                "metadata": {
                    "model": self.config.get("model_name"),
                    "tokens": self.model.last_token_count
                },
                "status": "success"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing directive with LM Studio: {e}")
            
            # Create error result
            error_result = {
                "output": f"Error: {str(e)}",
                "status": "error",
                "error": str(e)
            }
            
            return error_result
    
    def update_state(self, state: Dict[str, Any]) -> None:
        """
        Update the adapter state based on orchestration state.
        
        Args:
            state: State dictionary
        """
        if not self.initialized:
            raise RuntimeError("LM Studio adapter not initialized")
        
        # Update chat history if provided
        if "chat_history" in state:
            self.chat.history = state["chat_history"]
    
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the adapter.
        
        Returns:
            Capabilities dictionary
        """
        return {
            "name": "lmstudio",
            "description": "Adapter for LM Studio Python SDK",
            "version": "0.1.0",
            "features": ["text_generation", "chat", "callbacks"]
        }
