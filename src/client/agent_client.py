"""
HTTP Client for Agent Server - Pure business logic, no output handling.

Connects to a running agent server via HTTP and provides a clean interface.
Supports both regular and streaming responses.

Event callbacks allow callers to handle output presentation.
Events are returned as StreamEvent objects with types:
- TOOL_CALL: Agent is calling a tool
- TOOL_RESULT: Result from a tool
- CHUNK: Final response text from agent
- COMPLETE: Stream is complete
- ERROR: An error occurred
"""
import asyncio
import httpx
import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, AsyncGenerator, Callable, Optional


class EventType(str, Enum):
    """Types of events that can occur during agent communication"""
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    CHUNK = "chunk"
    COMPLETE = "complete"
    ERROR = "error"
    TOOL_PHASE_START = "tool_phase_start"  # Emitted by client when tool phase begins
    TOOL_PHASE_END = "tool_phase_end"      # Emitted by client when tool phase ends


@dataclass
class StreamEvent:
    """Represents a single event in the response stream"""
    type: EventType
    content: str = ""
    
    def __repr__(self) -> str:
        return f"StreamEvent(type={self.type}, content={self.content!r})"


class AgentClient:
    """
    HTTP client for the agent RPC server.
    
    The agent server runs separately and keeps no state.
    This client maintains the message history and allowed directories.
    
    Supports both:
    - Non-streaming: run() - returns complete response text
    - Streaming: run_stream() - yields StreamEvent objects as they arrive
    
    Callers must handle event routing/presentation themselves.
    No print statements or Rich output in this class.
    """
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=300.0)
        self.message_history = ""  # encoded json
    
    async def health_check(self) -> bool:
        """Check if the agent server is running"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except Exception:
            return False

    def clear_history(self):
        """Clear the message history"""
        self.message_history = ""
    
    async def run(self, prompt: str) -> str:
        """
        Send a prompt to the agent server and wait for complete response.
        
        Args:
            prompt: The user's prompt
        
        Returns:
            The complete response text from the agent
        
        Raises:
            Exception: If communication with server fails
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
                raise Exception(f"Server returned {response.status_code}: {response.text}")
            
            data = response.json()
            output = data.get("output", "")
            if data.get("message_history", "") != "":
                self.message_history = data.get("message_history", "")
            return output
        
        except httpx.ConnectError as e:
            raise Exception("Could not connect to agent server") from e
        except Exception as e:
            raise Exception(f"Error communicating with agent: {e}") from e

    async def run_stream(self, prompt: str) -> AsyncGenerator[StreamEvent, None]:
        """
        Send a prompt to the agent server with streaming response.
        
        Uses Server-Sent Events (SSE) to stream chunks as they arrive.
        
        Args:
            prompt: The user's prompt
        
        Yields:
            StreamEvent objects representing tool calls, results, response chunks, etc.
        
        Raises:
            Exception: If communication with server fails
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
                    yield StreamEvent(
                        type=EventType.ERROR,
                        content=f"Server returned {response.status_code}"
                    )
                    return
                
                # Track if we're currently in a tool phase
                in_tool_phase = False
                
                # Process Server-Sent Events
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    
                    if line.startswith("data: "):
                        try:
                            event_data = json.loads(line[6:])  # Strip "data: " prefix
                            event_type = event_data.get("type")
                            content = event_data.get("content", "")
                            
                            if event_type == "tool_call":
                                # Mark start of tool phase if not already
                                if not in_tool_phase:
                                    in_tool_phase = True
                                    yield StreamEvent(type=EventType.TOOL_PHASE_START)
                                
                                yield StreamEvent(type=EventType.TOOL_CALL, content=content)
                            
                            elif event_type == "tool_result":
                                yield StreamEvent(type=EventType.TOOL_RESULT, content=content)
                            
                            elif event_type == "chunk":
                                # Mark end of tool phase when we get actual response chunks
                                if in_tool_phase:
                                    in_tool_phase = False
                                    yield StreamEvent(type=EventType.TOOL_PHASE_END)
                                
                                yield StreamEvent(type=EventType.CHUNK, content=content)
                            
                            elif event_type == "complete":
                                # End tool phase if still active
                                if in_tool_phase:
                                    in_tool_phase = False
                                    yield StreamEvent(type=EventType.TOOL_PHASE_END)
                                
                                self.message_history = content
                                yield StreamEvent(type=EventType.COMPLETE, content=content)
                            
                            elif event_type == "error":
                                yield StreamEvent(type=EventType.ERROR, content=content)
                        
                        except json.JSONDecodeError as e:
                            yield StreamEvent(
                                type=EventType.ERROR,
                                content=f"Failed to parse event: {e}"
                            )

        except httpx.ConnectError:
            yield StreamEvent(
                type=EventType.ERROR,
                content="Could not connect to agent server"
            )
        except Exception as e:
            yield StreamEvent(
                type=EventType.ERROR,
                content=f"Error communicating with agent: {e}"
            )

    async def add_allowed_dir(self, dir_path: str) -> dict[str, Any]:
        """
        Add a directory to the allowed paths on the agent server.
        
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

