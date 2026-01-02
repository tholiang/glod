"""
HTTP Client for Agent Server.

Connects to a running agent server via HTTP and provides a clean interface.
Supports both regular and streaming responses.

The client maintains a persistent list of allowed directories that it sends
to the server on each restart.
"""
import httpx
import json
import sys
from pathlib import Path
from typing import Any, AsyncGenerator

from pydantic_ai import ModelMessage, ModelMessagesTypeAdapter


class AgentClient:
    """
    HTTP client for the agent RPC server.
    
    The agent server runs separately and keeps no state.
    This client maintains the message history and allowed directories.
    
    Allowed directories are persisted to disk and re-sent to the server
    on reconnection.
    
    Supports both:
    - Non-streaming: run() - waits for complete response
    - Streaming: run_stream() - yields chunks as they arrive
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=300.0)
        self.message_history = "" # encoded json
    
    async def health_check(self) -> bool:
        """Check if the agent server is running"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception as e:
            print(f"[Agent] Health check failed: {e}", file=sys.stderr)
            return False

    def clear_history(self):
        """Clear the message history"""
        self.message_history = ""
    
    async def run(self, prompt: str) -> None:
        """
        Send a prompt to the agent server and wait for complete response.
        
        Args:
            prompt: The user's prompt
        
        Outputs the response directly to stdout and updates message history.
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
                return
            
            data = response.json()
            print(data.get("output", ""))
            self.message_history = data.get("message_history", "")
        
        except httpx.ConnectError:
            print(f"error: could not connect to agent server")
        except Exception as e:
            print(f"error: error communicating with agent: {e}")
    
    async def run_stream(self, prompt: str) -> None:
        """
        Send a prompt to the agent server with streaming response.
        
        Uses Server-Sent Events (SSE) to stream chunks as they arrive.
        
        Args:
            prompt: The user's prompt
        
        Outputs chunks directly to stdout and updates message history at the end.
        """
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/run-stream",
                json={
                    "prompt": prompt,
                    "message_history": self.message_history
                }
            ) as response:
                
                if response.status_code != 200:
                    print(f"error: server returned {response.status_code}")
                    return
                
                # Process Server-Sent Events
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    
                    if line.startswith("data: "):
                        try:
                            event_data = json.loads(line[6:])  # Strip "data: " prefix
                            event_type = event_data.get("type")
                            content = event_data.get("content", "")
                            
                            if event_type == "chunk":
                                # Output response chunks directly
                                print(content, end="", flush=True)
                            elif event_type == "tool_call":
                                # Could format tool calls differently if desired
                                print(content, end="", flush=True)
                            
                            elif event_type == "tool_result":
                                print(content, end="", flush=True)
                            
                            elif event_type == "complete":
                                self.message_history = content
                                print()  # Final newline
                            
                            elif event_type == "error":
                                print(f"\nerror: {content}", file=sys.stderr)
                        
                        except json.JSONDecodeError as e:
                            print(f"error: failed to parse event: {e}", file=sys.stderr)

        except httpx.ConnectError:
            print(f"error: could not connect to agent server")
        except Exception as e:
            print(f"error: error communicating with agent: {e}")


    async def add_allowed_dir(self, dir_path: str) -> dict[str, Any]:
        """
        Add a directory to the allowed paths on the agent server.
        Also persists it locally so it survives server restarts.
        
        Args:
            dir_path: The directory path to allow
        
        Returns:
            Response dict with status and message
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/add-allowed-dir",
                json={"path": dir_path}
            )
            
            if response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Server returned {response.status_code}: {response.text}"
                }
            
            return response.json()
        
        except httpx.ConnectError:
            return {
                "status": "error",
                "message": "Could not connect to agent server"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }