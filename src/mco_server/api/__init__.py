"""
API Gateway for MCO Server

This module provides the REST API for MCO Server,
preserving the original Percertain DSL structure and progressive revelation approach.
"""

from typing import Dict, Any, Optional, List
import logging
import uuid
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from ..config import ConfigManager
from ..state import StateManager
from ..orchestrator import Orchestrator
from ..evaluator import SuccessCriteriaEvaluator
from ..adapters import get_adapter_by_name, BaseAdapter

logger = logging.getLogger(__name__)

# API models
class StartOrchestrationRequest(BaseModel):
    """Request model for starting an orchestration."""
    config_dir: str = Field(..., description="Directory containing MCO configuration files")
    adapter_name: str = Field(..., description="Name of the adapter to use")
    adapter_config: Dict[str, Any] = Field(default_factory=dict, description="Adapter configuration")
    initial_state: Dict[str, Any] = Field(default_factory=dict, description="Initial state variables")

class StartOrchestrationResponse(BaseModel):
    """Response model for starting an orchestration."""
    orchestration_id: str = Field(..., description="ID of the created orchestration")

class DirectiveResponse(BaseModel):
    """Response model for getting a directive."""
    type: str = Field(..., description="Type of directive (execute or complete)")
    step_id: Optional[str] = Field(None, description="ID of the step")
    instruction: Optional[str] = Field(None, description="Task instruction")
    guidance: Optional[str] = Field(None, description="Additional guidance")
    step_index: Optional[int] = Field(None, description="Index of the current step")
    total_steps: Optional[int] = Field(None, description="Total number of steps")
    persistent_context: Optional[Dict[str, Any]] = Field(None, description="Persistent context")
    injected_context: Optional[Dict[str, Any]] = Field(None, description="Injected context")

class ExecuteDirectiveRequest(BaseModel):
    """Request model for executing a directive."""
    result: Dict[str, Any] = Field(..., description="Result of executing the directive")

class ExecuteDirectiveResponse(BaseModel):
    """Response model for executing a directive."""
    result: Dict[str, Any] = Field(..., description="Result of executing the directive")
    evaluation: Dict[str, Any] = Field(..., description="Evaluation of the result")

class OrchestrationStatusResponse(BaseModel):
    """Response model for getting orchestration status."""
    orchestration_id: str = Field(..., description="ID of the orchestration")
    status: str = Field(..., description="Status of the orchestration")
    current_step_index: int = Field(..., description="Index of the current step")
    completed_steps: List[str] = Field(..., description="List of completed step IDs")
    total_steps: int = Field(..., description="Total number of steps")
    progress: float = Field(..., description="Progress as a fraction (0.0 to 1.0)")

class APIGateway:
    """
    API Gateway for MCO Server.
    
    Provides a REST API for interacting with MCO Server,
    preserving the original Percertain DSL structure and progressive revelation approach.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        state_manager: StateManager,
        orchestrator: Orchestrator
    ):
        """Initialize the API gateway."""
        self.config_manager = config_manager
        self.state_manager = state_manager
        self.orchestrator = orchestrator
        self.app = FastAPI(title="MCO Server API", version="0.1.0")
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self) -> None:
        """Register API routes."""
        app = self.app
        
        @app.post("/api/v1/orchestration", response_model=StartOrchestrationResponse)
        async def start_orchestration(request: StartOrchestrationRequest):
            """Start a new orchestration."""
            try:
                # Load configuration
                self.config_manager.load_from_directory(request.config_dir)
                
                # Get adapter
                adapter = get_adapter_by_name(request.adapter_name)
                if not adapter:
                    raise HTTPException(status_code=400, detail=f"Adapter not found: {request.adapter_name}")
                
                # Initialize adapter
                adapter.initialize(request.adapter_config)
                
                # Generate orchestration ID
                orchestration_id = str(uuid.uuid4())
                
                # Initialize state
                self.state_manager.initialize_state(orchestration_id, request.initial_state)
                
                # Start orchestration
                self.orchestrator.start_orchestration(orchestration_id, adapter)
                
                return {"orchestration_id": orchestration_id}
                
            except Exception as e:
                logger.error(f"Error starting orchestration: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/v1/orchestration/{orchestration_id}/directive", response_model=DirectiveResponse)
        async def get_directive(orchestration_id: str):
            """Get the next directive for an orchestration."""
            try:
                directive = self.orchestrator.get_next_directive(orchestration_id)
                return directive
                
            except Exception as e:
                logger.error(f"Error getting directive: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.post("/api/v1/orchestration/{orchestration_id}/execute", response_model=ExecuteDirectiveResponse)
        async def execute_directive(orchestration_id: str, request: ExecuteDirectiveRequest):
            """Execute the current directive for an orchestration."""
            try:
                # Process result
                evaluation = self.orchestrator.process_result(orchestration_id, request.result)
                
                return {
                    "result": request.result,
                    "evaluation": evaluation
                }
                
            except Exception as e:
                logger.error(f"Error executing directive: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @app.get("/api/v1/orchestration/{orchestration_id}", response_model=OrchestrationStatusResponse)
        async def get_status(orchestration_id: str):
            """Get the status of an orchestration."""
            try:
                status = self.orchestrator.get_status(orchestration_id)
                return status
                
            except Exception as e:
                logger.error(f"Error getting status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    def start(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """
        Start the API server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)
