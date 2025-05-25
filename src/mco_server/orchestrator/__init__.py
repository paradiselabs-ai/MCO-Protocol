"""
Orchestrator for MCO Server

This module provides the core orchestration functionality for MCO Server,
preserving the original Percertain DSL structure and progressive revelation approach.
"""

from typing import Dict, Any, Optional, List
import logging
from ..config import ConfigManager
from ..state import StateManager
from ..evaluator import SuccessCriteriaEvaluator
from ..adapters import BaseAdapter

logger = logging.getLogger(__name__)

class Orchestrator:
    """
    Orchestrates the execution of workflows based on MCO configuration.
    Preserves the progressive revelation structure and handles persistent vs. injected components.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        state_manager: StateManager,
        evaluator: SuccessCriteriaEvaluator
    ):
        """Initialize the orchestrator with all necessary components."""
        self.config_manager = config_manager
        self.state_manager = state_manager
        self.evaluator = evaluator
        self.adapters = {}
        self.current_directives = {}
    
    def start_orchestration(self, orchestration_id: str, adapter: BaseAdapter) -> None:
        """
        Start a new orchestration.
        
        Args:
            orchestration_id: ID of the orchestration
            adapter: Adapter instance to use for execution
        """
        # Register adapter for this orchestration
        self.adapters[orchestration_id] = adapter
        
        # Initialize state if not already initialized
        if not self.state_manager.get_state(orchestration_id):
            self.state_manager.initialize_state(orchestration_id, {})
        
        # Set status to started
        self.state_manager.update_state(orchestration_id, {"status": "started"})
        
        logger.info(f"Started orchestration {orchestration_id}")
    
    def get_next_directive(self, orchestration_id: str) -> Dict[str, Any]:
        """
        Get the next directive for an orchestration.
        Implements the progressive revelation structure.
        """
        # Get current state
        state = self.state_manager.get_state(orchestration_id)
        
        # Check if orchestration is complete
        if state.get("status") == "completed":
            return {"type": "complete", "message": "Orchestration complete"}
        
        # Get workflow steps
        steps = self.config_manager.get_workflow_steps()
        if not steps:
            logger.warning(f"No workflow steps defined for orchestration {orchestration_id}")
            return {"type": "error", "message": "No workflow steps defined"}
        
        # Get current step index
        current_step_index = state.get("current_step_index", 0)
        
        # Check if all steps are complete
        if current_step_index >= len(steps):
            self.state_manager.update_state(orchestration_id, {"status": "completed"})
            return {"type": "complete", "message": "All steps complete"}
        
        # Get current step
        current_step = steps[current_step_index]
        
        # Create directive with persistent context (core + sc)
        directive = {
            "type": "execute",
            "step_id": current_step.get("id", f"step_{current_step_index}"),
            "instruction": self._substitute_variables(
                current_step.get("task", ""),
                state.get("variables", {})
            ),
            "step_index": current_step_index,
            "total_steps": len(steps),
            
            # Add persistent context
            "persistent_context": {
                "core": self.config_manager.get_core_config(),
                "success_criteria": self.config_manager.get_success_criteria(),
                "goal": self.config_manager.get_goal(),
                "target_audience": self.config_manager.get_target_audience(),
                "developer_vision": self.config_manager.get_developer_vision()
            }
        }
        
        # Add strategic injections based on step type
        step_type = current_step.get("type", "default")
        
        if step_type == "feature_implementation":
            # Inject features for this step
            directive["injected_context"] = {
                "features": self.config_manager.get_features()
            }
        elif step_type == "styling":
            # Inject styles for this step
            directive["injected_context"] = {
                "styles": self.config_manager.get_styles()
            }
        
        # Add guidance based on success criteria and target audience
        directive["guidance"] = self._get_guidance_for_step(current_step)
        
        # Store current directive
        self.current_directives[orchestration_id] = directive
        
        return directive
    
    def execute_current_directive(self, orchestration_id: str) -> Dict[str, Any]:
        """
        Execute the current directive for an orchestration.
        
        Args:
            orchestration_id: ID of the orchestration
            
        Returns:
            Result dictionary
        """
        # Get current directive
        directive = self.current_directives.get(orchestration_id)
        if not directive:
            logger.warning(f"No current directive for orchestration {orchestration_id}")
            return {"status": "error", "message": "No current directive"}
        
        # Get adapter
        adapter = self.adapters.get(orchestration_id)
        if not adapter:
            logger.warning(f"No adapter registered for orchestration {orchestration_id}")
            return {"status": "error", "message": "No adapter registered"}
        
        # Execute directive
        try:
            result = adapter.execute_directive(directive)
            
            # Evaluate result
            evaluation = self._evaluate_result(orchestration_id, directive, result)
            
            # Update state based on evaluation
            if evaluation["success"]:
                # Mark step as complete
                self.state_manager.mark_step_complete(orchestration_id, directive["step_id"])
                
                # Move to next step
                self.state_manager.set_current_step(
                    orchestration_id,
                    directive["step_index"] + 1
                )
            
            # Return result with evaluation
            return {
                "result": result,
                "evaluation": evaluation
            }
            
        except Exception as e:
            logger.error(f"Error executing directive: {e}")
            return {
                "status": "error",
                "message": f"Error executing directive: {str(e)}"
            }
    
    def process_result(self, orchestration_id: str, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a result for an orchestration.
        
        Args:
            orchestration_id: ID of the orchestration
            result: Result dictionary
            
        Returns:
            Evaluation dictionary
        """
        # Get current directive
        directive = self.current_directives.get(orchestration_id)
        if not directive:
            logger.warning(f"No current directive for orchestration {orchestration_id}")
            return {"success": False, "message": "No current directive"}
        
        # Evaluate result
        evaluation = self._evaluate_result(orchestration_id, directive, result)
        
        # Update state based on evaluation
        if evaluation["success"]:
            # Mark step as complete
            self.state_manager.mark_step_complete(orchestration_id, directive["step_id"])
            
            # Move to next step
            self.state_manager.set_current_step(
                orchestration_id,
                directive["step_index"] + 1
            )
        
        return evaluation
    
    def get_status(self, orchestration_id: str) -> Dict[str, Any]:
        """
        Get the status of an orchestration.
        
        Args:
            orchestration_id: ID of the orchestration
            
        Returns:
            Status dictionary
        """
        # Get current state
        state = self.state_manager.get_state(orchestration_id)
        
        # Get workflow steps
        steps = self.config_manager.get_workflow_steps()
        
        # Calculate progress
        total_steps = len(steps) if steps else 0
        completed_steps = len(state.get("completed_steps", []))
        progress = completed_steps / total_steps if total_steps > 0 else 0.0
        
        # Create status dictionary
        status = {
            "orchestration_id": orchestration_id,
            "status": state.get("status", "unknown"),
            "current_step_index": state.get("current_step_index", 0),
            "completed_steps": state.get("completed_steps", []),
            "total_steps": total_steps,
            "progress": progress
        }
        
        return status
    
    def _evaluate_result(
        self,
        orchestration_id: str,
        directive: Dict[str, Any],
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate a result against success criteria.
        
        Args:
            orchestration_id: ID of the orchestration
            directive: Directive dictionary
            result: Result dictionary
            
        Returns:
            Evaluation dictionary
        """
        # Get success criteria
        success_criteria = self.config_manager.get_success_criteria()
        
        # Get workflow steps
        steps = self.config_manager.get_workflow_steps()
        
        # Create step config for evaluator
        step_config = {
            "steps": steps,
            "current_step_index": directive["step_index"],
            "success_condition": directive["step_id"]  # Use step_id as success condition
        }
        
        # Evaluate result
        evaluation = self.evaluator.evaluate(
            directive["step_id"],
            result,
            success_criteria,
            step_config
        )
        
        return evaluation
    
    def _get_guidance_for_step(self, step: Dict[str, Any]) -> str:
        """
        Get guidance for a step based on success criteria, target audience, and developer vision.
        
        Args:
            step: Step dictionary
            
        Returns:
            Guidance string
        """
        # Get success condition
        success_condition = step.get("id")
        if not success_condition:
            return ""
        
        # Get success criteria
        success_criteria = self.config_manager.get_success_criteria()
        
        # Get target audience and developer vision
        target_audience = self.config_manager.get_target_audience()
        developer_vision = self.config_manager.get_developer_vision()
        goal = self.config_manager.get_goal()
        
        # Create guidance
        guidance = []
        
        if goal:
            guidance.append(f"Goal: {goal}")
        
        if target_audience:
            guidance.append(f"Target Audience: {target_audience}")
        
        if developer_vision:
            guidance.append(f"Developer Vision: {developer_vision}")
        
        # Add specific success criteria
        if "success_criteria" in success_criteria:
            criteria_items = success_criteria["success_criteria"]
            if isinstance(criteria_items, list):
                guidance.append("Success Criteria:")
                for item in criteria_items:
                    guidance.append(f"- {item}")
        
        return "\n\n".join(guidance)
    
    def _substitute_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """
        Substitute variables in a text string.
        
        Args:
            text: Text string with variable placeholders
            variables: Dictionary of variables
            
        Returns:
            Text with variables substituted
        """
        if not text:
            return text
        
        result = text
        
        # Replace {variable} placeholders
        for name, value in variables.items():
            placeholder = f"{{{name}}}"
            if isinstance(value, (list, dict)):
                # Convert complex types to string representation
                str_value = str(value)
            else:
                str_value = str(value)
            
            result = result.replace(placeholder, str_value)
        
        return result
