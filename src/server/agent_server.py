"""
Agent RPC Server - Run this as a separate process/service.

Provides HTTP endpoints for:
- /run - Process a prompt with message history (non-streaming)
- /run-stream - Process a prompt with streaming response (Server-Sent Events)
- /health - Health check endpoint

Start it with: python -m server.agent_server
"""
from dataclasses import dataclass, asdict
import json
import os
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

from pydantic_ai import Agent, ModelMessage, ModelMessagesTypeAdapter
from pydantic_ai.models.anthropic import AnthropicModel

from server.agents.editor import editor_run, editor_run_stream
from server.app import get_app

server = FastAPI(title="Glod Agent Server")

class RunRequest(BaseModel):
    """Request to run the agent"""
    prompt: str
    message_history: str = ""

class RunResponse(BaseModel):
    """Response from running the agent"""
    output: str
    message_history: str = ""
    status: str = "success"
    error: str | None = None

class StreamEvent(BaseModel):
    """A single event in the stream"""
    type: str  # "chunk", "tool_call", "tool_result", "complete", "error"
    content: str
    
    def to_sse(self) -> str:
        """Convert to Server-Sent Event format"""
        return f"data: {json.dumps(self.model_dump())}\n\n"


def _serialize_message_history(message_history: list[ModelMessage]) -> str:
    return ModelMessagesTypeAdapter.dump_json(message_history).decode()

def _deserialize_message_history(message_history: str) -> list[ModelMessage]:
    if message_history == "":
        return []
    return ModelMessagesTypeAdapter.validate_json(message_history)

async def _process_request(prompt: str, message_history: str) -> str:
    """Process a single prompt with the agent"""
    try:
        result = await editor_run(prompt, message_history=_deserialize_message_history(message_history))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _stream_generator(prompt: str, message_history: str) -> AsyncGenerator[str]:
    """
    Generator that yields Server-Sent Events as the agent streams responses.
    
    Yields JSON-formatted events that can be parsed by the client.
    """
    try:
        deserialized_history = _deserialize_message_history(message_history)
        # Process the stream
        async for event_type, content in editor_run_stream(prompt, deserialized_history):
            # Emit properly typed events
            event = StreamEvent(type=event_type, content=content)
            yield event.to_sse()
        
        # Send completion event with final message history
        completion_event = StreamEvent(
            type="complete",
            content=_serialize_message_history(deserialized_history)
        )
        yield completion_event.to_sse()
        
    except Exception as e:
        error_event = StreamEvent(type="error", content=str(e))
        yield error_event.to_sse()


@server.post("/run", response_model=RunResponse)
async def run(request: RunRequest) -> RunResponse:
    """Run the agent with a prompt (non-streaming)"""
    message_history = request.message_history
    output = await _process_request(request.prompt, message_history)
    return RunResponse(output=output, message_history=message_history, status="success")


@server.post("/run-stream")
async def run_stream(request: RunRequest) -> StreamingResponse:
    """
    Run the agent with streaming response using Server-Sent Events (SSE).
    
    Returns a stream of JSON events with types:
    - "chunk": A piece of the response text
    - "tool_call": When the agent calls a tool
    - "tool_result": The result from a tool call
    - "complete": Final event with updated message history
    - "error": If an error occurs
    """
    return StreamingResponse(
        _stream_generator(request.prompt, request.message_history),
        media_type="text/event-stream"
    )


class AddAllowedDirRequest(BaseModel):
    """Request to add an allowed directory"""
    path: str


@server.post("/add-allowed-dir")
async def add_allowed_dir(request: AddAllowedDirRequest) -> dict[str, str]:
    """Add a directory to the allowed paths for the agent"""
    try:
        dir_path = Path(request.path)
        if not dir_path.exists():
            raise HTTPException(status_code=400, detail=f"Directory does not exist: {request.path}")
        if not dir_path.is_dir():
            raise HTTPException(status_code=400, detail=f"Path is not a directory: {request.path}")
        
        app = get_app()
        app.allow_path(dir_path)

        return {
            "status": "success",
            "message": f"Added allowed directory: {request.path}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@server.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "server.agent_server:server",
        host="127.0.0.1",
        port=8000,
        reload=False
    )