"""
Mock LM Studio SDK for testing
"""

class MockLMStudioResponse:
    """Mock response from LM Studio SDK."""
    
    def __init__(self, output="Test output", status="success"):
        self.output = output
        self.metadata = {
            "model": "test-model",
            "tokens": 10.5
        }
        self.status = status

class MockLMStudioSDK:
    """Mock LM Studio SDK for testing."""
    
    def __init__(self, model_name="test-model"):
        self.model_name = model_name
        
    def generate(self, prompt, **kwargs):
        """Mock generate method."""
        return {
            "result": {
                "output": f"I've received your task and will work on it.\nI've analyzed the core configuration and understand the workflow structure.\nI'll ensure my response meets the specified success criteria.\nI understand the overall goal of this project.\nI'll tailor my response for the specified target audience.\nI'll align my work with the developer's vision for this project.\n\nTask completed successfully. Here's the output:\n\n```\n{{\"result\": \"success\", \"data\": {{\"key\": \"value\"}}}}\n```",
                "metadata": {
                    "model": self.model_name,
                    "tokens": 89.7
                },
                "status": "success"
            }
        }
