"""
Client for interacting with the agent via HTTP RPC.

The agent server runs separately. This client:
- Manages message history
- Handles user interaction
- Communicates with agent via HTTP
"""
from pathlib import Path
import asyncio
import sys

from pydantic_ai.messages import ModelMessage
from client_agent import AgentClient
from app import App, get_app


async def _entry(prompt: str, agent_client: AgentClient) -> None:
    """Send request to agent and display response"""
    await agent_client.run(prompt)


def _command(prompt: str, agent_client: AgentClient) -> int:
    """Handle commands starting with /"""
    stripped = prompt.strip()[1:].lower()
    
    if stripped == "exit":
        return 1
    elif stripped == "clear":
        agent_client.clear_history()
        print("Message history cleared.\n")
    elif stripped == "help":
        print("""
Available commands:
  /exit      - Exit the program
  /clear     - Clear message history
  /help      - Show this help message

Make sure the agent server is running:
  python -m agents.agent_server
        """)
    else:
        print(f"Unknown command: {prompt}")
    
    return 0


async def _run():
    app = get_app()
    app.allow_path(Path("/Users/thomasliang/Documents/Programs/glod"))
    
    # Initialize client and agent client
    agent_client = AgentClient()
    
    # Check if agent server is running
    if not await agent_client.health_check():
        print("❌ Agent server is not running!")
        print("Start it with: python -m agents.agent_server")
        return
    
    print("✅ Connected to agent server!")
    print("Type /help for commands.\n")
    
    while True:
        prompt = input("> ")
        if prompt.startswith("/"):
            if _command(prompt, agent_client) == 1:
                break
            continue

        # Run agent and display response
        await _entry(prompt, agent_client)


def _run_sync():
    """Wrapper to run async code from sync context"""
    asyncio.run(_run())


if __name__ == "__main__":
    _run_sync()

