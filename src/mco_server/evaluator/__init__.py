"""
Success Criteria Evaluator for MCO Server

This module provides functionality for evaluating success criteria against results,
preserving the original Percertain DSL structure and progressive revelation approach.
"""

from typing import Dict, Any, List, Optional
import re
import logging

logger = logging.getLogger(__name__)

class SuccessCriteriaEvaluator:
    """
    Evaluates success criteria against execution results.
    Preserves the original success criteria structure including developer vision and target audience.
    """
    
    def __init__(self):
        """Initialize the success criteria evaluator."""
        pass
    
    def evaluate(
        self,
        step_id: str,
        result: Dict[str, Any],
        success_criteria: Dict[str, Any],
        step_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate success criteria for a step.
        Includes developer vision and target audience considerations.
        
        Args:
            step_id: ID of the step
            result: Result dictionary from execution
            success_criteria: Success criteria configuration
            step_config: Step configuration
            
        Returns:
            Evaluation dictionary
        """
        # Get success condition for this step
        success_condition = step_config.get("success_condition")
        if not success_condition:
            logger.warning(f"No success condition defined for step {step_id}")
            return {
                "success": False,
                "feedback": "No success condition defined for this step",
                "progress": 0.0
            }
        
        # Get developer vision and target audience
        developer_vision = success_criteria.get("developer_vision", "")
        target_audience = success_criteria.get("target_audience", "")
        goal = success_criteria.get("goal", "")
        
        # Get success criteria items
        criteria_items = []
        if "success_criteria" in success_criteria:
            if isinstance(success_criteria["success_criteria"], list):
                criteria_items = success_criteria["success_criteria"]
        
        # Check if result meets the criteria
        output = result.get("output", "")
        status = result.get("status", "")
        
        # Basic checks
        if status == "error":
            return {
                "success": False,
                "feedback": f"Error: {result.get('error', 'Unknown error')}",
                "progress": 0.0
            }
        
        # Check for explicit success indicators in output
        success_indicators = [
            r"(?i)success:",
            r"(?i)completed successfully",
            r"(?i)task complete",
            r"(?i)criteria met"
        ]
        
        for indicator in success_indicators:
            match = re.search(indicator, output)
            if match:
                # Extract feedback after the indicator
                feedback_match = re.search(f"{indicator}(.*?)(?:\n|$)", output, re.DOTALL)
                feedback = feedback_match.group(1).strip() if feedback_match else "Success detected in output"
                
                # Calculate progress
                total_steps = len(step_config.get("steps", []))
                current_step = step_config.get("current_step_index", 0) + 1
                progress = current_step / total_steps if total_steps > 0 else 0.0
                
                return {
                    "success": True,
                    "feedback": feedback,
                    "progress": progress,
                    "context": {
                        "goal": goal,
                        "target_audience": target_audience,
                        "developer_vision": developer_vision
                    }
                }
        
        # Check for explicit failure indicators
        failure_indicators = [
            r"(?i)failure:",
            r"(?i)failed to",
            r"(?i)criteria not met",
            r"(?i)unsuccessful"
        ]
        
        for indicator in failure_indicators:
            match = re.search(indicator, output)
            if match:
                # Extract feedback after the indicator
                feedback_match = re.search(f"{indicator}(.*?)(?:\n|$)", output, re.DOTALL)
                feedback = feedback_match.group(1).strip() if feedback_match else "Failure detected in output"
                
                return {
                    "success": False,
                    "feedback": feedback,
                    "progress": 0.0,
                    "context": {
                        "goal": goal,
                        "target_audience": target_audience,
                        "developer_vision": developer_vision
                    }
                }
        
        # Check against specific success criteria items
        if criteria_items:
            # Count how many criteria items are mentioned in the output
            criteria_met = 0
            for criterion in criteria_items:
                if isinstance(criterion, str) and criterion.lower() in output.lower():
                    criteria_met += 1
            
            # If at least half of the criteria are met, consider it a success
            if criteria_met >= len(criteria_items) / 2:
                # Calculate progress
                total_steps = len(step_config.get("steps", []))
                current_step = step_config.get("current_step_index", 0) + 1
                progress = current_step / total_steps if total_steps > 0 else 0.0
                
                return {
                    "success": True,
                    "feedback": f"Success: {criteria_met} out of {len(criteria_items)} criteria met",
                    "progress": progress,
                    "context": {
                        "goal": goal,
                        "target_audience": target_audience,
                        "developer_vision": developer_vision
                    }
                }
        
        # Default to success if no failure detected and no specific criteria to check
        # Calculate progress
        total_steps = len(step_config.get("steps", []))
        current_step = step_config.get("current_step_index", 0) + 1
        progress = current_step / total_steps if total_steps > 0 else 0.0
        
        return {
            "success": True,
            "feedback": "Success: Task completed without explicit failure indicators",
            "progress": progress,
            "context": {
                "goal": goal,
                "target_audience": target_audience,
                "developer_vision": developer_vision
            }
        }
