"""
Agent RPC Server - Run this as a separate process/service.

Provides HTTP endpoints for:
- /run - Process a prompt with message history
- /clear - Clear message history on the server

Start it with: python -m agents.agent_server
"""
import asyncio
from typing import Any, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from pydantic_ai import Agent, ModelMessage
from pydantic_ai.models.anthropic import AnthropicModel

from tools import files
from agents.editor import editor_run, editor_run_stream

app = FastAPI(title="Glod Agent Server")

class RunRequest(BaseModel):
    """Request to run the agent"""
    prompt: str
    message_history: list[ModelMessage] = []


class RunResponse(BaseModel):
    """Response from running the agent"""
    output: str
    message_history: list[ModelMessage] = []
    status: str = "success"
    error: str | None = None

async def _process_request(prompt: str, message_history: list[ModelMessage]) -> str:
    """Process a single prompt with the agent"""
    try:
        result = await editor_run(prompt, message_history=message_history)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/run", response_model=RunResponse)
async def run(request: RunRequest) -> RunResponse:
    """Run the agent with a prompt"""
    message_history = request.message_history
    output = await _process_request(request.prompt, message_history)
    return RunResponse(output=output, message_history=message_history, status="success")


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "agents.agent_server:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )

