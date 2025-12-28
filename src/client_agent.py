"""
HTTP Client for Agent Server.

Connects to a running agent server via HTTP and provides a clean interface.
"""
import httpx
import sys
from typing import Any

from pydantic_ai import ModelMessage


class AgentClient:
    """
    HTTP client for the agent RPC server.
    
    The agent server runs separately and keeps no state.
    This client maintains the message history.
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=300.0)

        self.message_history = []
    
    async def health_check(self) -> bool:
        """Check if the agent server is running"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            print(f"[Agent] Health check failed: {e}", file=sys.stderr)
            return False

    def clear_history(self):
        self.message_history = []
    
    async def run(
        self, 
        prompt: str
    ) -> None:
        """
        Send a prompt to the agent server.
        
        Args:
            prompt: The user's prompt
            message_history: Optional message history (currently not sent to agent)
        
        Returns:
            Response dict with 'output' and 'status'
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/run",
                json={
                    "prompt": prompt,
                    "message_history": self.message_history
                }
            )
            
            if response.status_code != 200:
                print(f"error: server returned {response.status_code} {response.text}")
            
            data = response.json()
            print(data.get("output", ""))
            self.message_history = data.get("message_history")
        
        except httpx.ConnectError:
            print(f"error: could not connect to agent server")
        except Exception as e:
            print(f"error: error communicating with agent: {e}")