"""
Success Criteria Evaluator for MCO Server

This module provides functionality for evaluating success criteria against results.
"""

from typing import Dict, Any, List, Optional
import re
import logging

logger = logging.getLogger(__name__)

class SuccessCriteriaEvaluator:
    """
    Evaluates success criteria against execution results.
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
        
        # Find matching criterion
        criterion = self._find_criterion(success_condition, success_criteria)
        if not criterion:
            logger.warning(f"No success criterion found for condition {success_condition}")
            return {
                "success": False,
                "feedback": f"No success criterion found for condition {success_condition}",
                "progress": 0.0
            }
        
        # Evaluate criterion
        evaluation = self._evaluate_criterion(criterion, result)
        
        # Calculate progress
        total_steps = len(step_config.get("steps", []))
        current_step = step_config.get("current_step_index", 0) + 1
        progress = current_step / total_steps if total_steps > 0 else 0.0
        
        # Create evaluation result
        evaluation_result = {
            "success": evaluation["success"],
            "feedback": evaluation["feedback"],
            "progress": progress,
            "criterion_id": criterion["id"],
            "details": evaluation.get("details", {})
        }
        
        logger.debug(f"Evaluated step {step_id}: {evaluation_result['success']}")
        return evaluation_result
    
    def _find_criterion(
        self,
        criterion_id: str,
        success_criteria: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Find a success criterion by ID.
        
        Args:
            criterion_id: ID of the criterion
            success_criteria: Success criteria configuration
            
        Returns:
            Criterion dictionary or None if not found
        """
        if "success_criteria" not in success_criteria:
            return None
        
        for criterion in success_criteria["success_criteria"]:
            if criterion.get("id") == criterion_id:
                return criterion
        
        return None
    
    def _evaluate_criterion(
        self,
        criterion: Dict[str, Any],
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Evaluate a success criterion against a result.
        
        Args:
            criterion: Criterion dictionary
            result: Result dictionary
            
        Returns:
            Evaluation dictionary
        """
        # Get evaluation method
        evaluation_method = criterion.get("evaluation", "")
        
        # Check if result meets the criterion
        output = result.get("output", "")
        status = result.get("status", "")
        
        # Basic checks
        if status == "error":
            return {
                "success": False,
                "feedback": f"Error: {result.get('error', 'Unknown error')}"
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
                
                return {
                    "success": True,
                    "feedback": feedback
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
                    "feedback": feedback
                }
        
        # If no explicit indicators, use evaluation method
        if evaluation_method:
            # Check if output contains the evaluation method
            if evaluation_method.lower() in output.lower():
                return {
                    "success": True,
                    "feedback": f"Success: {evaluation_method}"
                }
        
        # Default to success if no failure detected
        return {
            "success": True,
            "feedback": "Success: Task completed without explicit failure indicators"
        }
