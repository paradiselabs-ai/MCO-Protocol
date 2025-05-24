"""
API Gateway for MCO Server

This module provides a REST API for interacting with MCO Server.
"""

from typing import Dict, Any, Optional
import logging
import threading
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

logger = logging.getLogger(__name__)

class APIGateway:
    """
    Provides a REST API for MCO Server.
    """
    
    def __init__(self, server):
        """
        Initialize the API gateway.
        
        Args:
            server: MCO Server instance
        """
        self.server = server
        self.http_server = None
        self.server_thread = None
    
    def start_server(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """
        Start the API server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
        """
        if self.http_server:
            logger.warning("API server already running")
            return
        
        # Create request handler with access to MCO server
        mco_server = self.server
        
        class MCORequestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                try:
                    # Parse path and query parameters
                    parsed_url = urllib.parse.urlparse(self.path)
                    path = parsed_url.path
                    
                    # Handle routes
                    if path == "/api/v1/health":
                        self._handle_health()
                    elif path.startswith("/api/v1/orchestration/"):
                        orchestration_id = path.split("/")[-1]
                        if orchestration_id == "orchestration":
                            self._handle_list_orchestrations()
                        else:
                            self._handle_get_orchestration(orchestration_id)
                    else:
                        self._send_response(404, {"error": "Not found"})
                
                except Exception as e:
                    logger.error(f"Error handling GET request: {e}")
                    self._send_response(500, {"error": str(e)})
            
            def do_POST(self):
                try:
                    # Parse path
                    parsed_url = urllib.parse.urlparse(self.path)
                    path = parsed_url.path
                    
                    # Read request body
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length).decode("utf-8")
                    data = json.loads(body) if body else {}
                    
                    # Handle routes
                    if path == "/api/v1/orchestration":
                        self._handle_start_orchestration(data)
                    elif path.startswith("/api/v1/orchestration/"):
                        parts = path.split("/")
                        if len(parts) >= 5 and parts[-1] == "directive":
                            orchestration_id = parts[-2]
                            self._handle_get_next_directive(orchestration_id)
                        elif len(parts) >= 5 and parts[-1] == "execute":
                            orchestration_id = parts[-2]
                            self._handle_execute_directive(orchestration_id, data)
                        else:
                            self._send_response(404, {"error": "Not found"})
                    else:
                        self._send_response(404, {"error": "Not found"})
                
                except Exception as e:
                    logger.error(f"Error handling POST request: {e}")
                    self._send_response(500, {"error": str(e)})
            
            def _send_response(self, status_code: int, data: Dict[str, Any]) -> None:
                """Send JSON response."""
                self.send_response(status_code)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode("utf-8"))
            
            def _handle_health(self) -> None:
                """Handle health check endpoint."""
                self._send_response(200, {"status": "ok"})
            
            def _handle_list_orchestrations(self) -> None:
                """Handle list orchestrations endpoint."""
                # This is a placeholder - in a real implementation, we would list all orchestrations
                self._send_response(200, {"orchestrations": []})
            
            def _handle_get_orchestration(self, orchestration_id: str) -> None:
                """Handle get orchestration endpoint."""
                try:
                    status = mco_server.get_orchestration_status(orchestration_id)
                    # Convert non-serializable objects
                    serializable_status = {
                        k: v for k, v in status.items() 
                        if k not in ["state_manager", "config_manager"]
                    }
                    self._send_response(200, serializable_status)
                except Exception as e:
                    self._send_response(404, {"error": f"Orchestration not found: {str(e)}"})
            
            def _handle_start_orchestration(self, data: Dict[str, Any]) -> None:
                """Handle start orchestration endpoint."""
                try:
                    config_dir = data.get("config_dir")
                    adapter_name = data.get("adapter_name", "default")
                    adapter_config = data.get("adapter_config")
                    initial_state = data.get("initial_state")
                    
                    if not config_dir:
                        self._send_response(400, {"error": "config_dir is required"})
                        return
                    
                    orchestration_id = mco_server.start_orchestration(
                        config_dir=config_dir,
                        adapter_name=adapter_name,
                        adapter_config=adapter_config,
                        initial_state=initial_state
                    )
                    
                    self._send_response(200, {"orchestration_id": orchestration_id})
                except Exception as e:
                    self._send_response(500, {"error": f"Failed to start orchestration: {str(e)}"})
            
            def _handle_get_next_directive(self, orchestration_id: str) -> None:
                """Handle get next directive endpoint."""
                try:
                    directive = mco_server.get_next_directive(orchestration_id)
                    self._send_response(200, directive)
                except Exception as e:
                    self._send_response(500, {"error": f"Failed to get directive: {str(e)}"})
            
            def _handle_execute_directive(self, orchestration_id: str, data: Dict[str, Any]) -> None:
                """Handle execute directive endpoint."""
                try:
                    result = mco_server.execute_directive(orchestration_id)
                    self._send_response(200, result)
                except Exception as e:
                    self._send_response(500, {"error": f"Failed to execute directive: {str(e)}"})
        
        # Create and start HTTP server
        self.http_server = HTTPServer((host, port), MCORequestHandler)
        
        # Start server in a separate thread
        self.server_thread = threading.Thread(target=self.http_server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        logger.info(f"API server started on {host}:{port}")
    
    def stop_server(self) -> None:
        """Stop the API server."""
        if self.http_server:
            self.http_server.shutdown()
            self.http_server = None
            self.server_thread = None
            logger.info("API server stopped")
