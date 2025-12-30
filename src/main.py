"""
Client for interacting with the agent via HTTP RPC.

The agent server runs separately. This client:
- Manages message history
- Handles user interaction
- Communicates with agent via HTTP (with streaming support)
- Can start/stop/restart the agent server

Supports streaming responses for real-time output.
"""
import os
from pathlib import Path
import asyncio
import sys

from pydantic_ai.messages import ModelMessage
from client_agent import AgentClient
from server_manager import ServerManager


# Global server manager instance
server_manager = ServerManager(project_root=Path(__file__).parent.parent)


async def _entry(prompt: str, agent_client: AgentClient, stream: bool = True) -> None:
    """
    Send request to agent and display response.
    
    Args:
        prompt: The user's prompt
        agent_client: The agent client instance
        stream: Whether to use streaming response (default True)
    """
    if stream:
        await agent_client.run_stream(prompt)
    else:
        await agent_client.run(prompt)

def _exit() -> None:
    """
    Exit agent and close server.
    """
    server_manager.stop()


async def _command(prompt: str, agent_client: AgentClient) -> int:
    """
    Handle commands starting with /
    
    Returns:
        0 to continue, 1 to exit
    """
    stripped = prompt.strip()[1:].lower()
    parts = stripped.split(maxsplit=1)
    command = parts[0]
    
    if command == "exit":
        return 1
    elif command == "allow":
        if len(parts) > 1:
            await _handle_allow_dir_command(parts[1], agent_client)
        else:
            print("Usage: /allow <directory_path>")

    elif command == "clear":
        agent_client.clear_history()
        print("Message history cleared.\n")
    elif command == "server":
        _handle_server_command(parts[1] if len(parts) > 1 else None)
    elif command == "help":
        print("""
  /allow <path>           - Add a directory to allowed paths

Available commands:
  /exit                - Exit the program
  /clear               - Clear message history
  /server start        - Start the agent server
  /server stop         - Stop the agent server
  /server restart      - Restart the agent server
  /server status       - Check agent server status
  /help                - Show this help message
        """)
    else:
        print(f"Unknown command: /{command}")
    
    return 0

async def _handle_allow_dir_command(dir_path: str, agent_client: AgentClient) -> None:
    """Handle /allow commands to add allowed directories"""
    try:
        response = await agent_client.add_allowed_dir(dir_path)
        if response.get("status") == "success":
            print(f"✅ {response.get('message')}")
        else:
            print(f"❌ Error: {response}")
    except Exception as e:
        print(f"❌ Failed to add allowed directory: {str(e)}")

def _handle_server_command(subcommand: str | None) -> None:
    """Handle /server commands"""
    if subcommand is None:
        print("Usage: /server [start|stop|restart|status]")
        return

    subcommand = subcommand.lower()
    
    if subcommand == "start":
        server_manager.start()
    elif subcommand == "stop":
        server_manager.stop()
    elif subcommand == "restart":
        server_manager.restart()
    elif subcommand == "status":
        if server_manager.is_running():
            print(f"✅ Agent server is running (PID: {server_manager.get_pid()})")
        else:
            print("❌ Agent server is not running")
    else:
        print(f"Unknown server command: {subcommand}")
        print("Usage: /server [start|stop|restart|status]")


async def _run():
    # Initialize client and agent client
    agent_client = AgentClient()
    
    # Check if agent server is running
    if not await agent_client.health_check():
        print("❌ Agent server is not running!")
        print("Starting agent server automatically...\n")
        if not server_manager.start():
            print("Failed to start agent server. Exiting.")
            return
        
        # Give the server a moment to fully initialize
        await asyncio.sleep(1)
        
        # Check again
        if not await agent_client.health_check():
            print("❌ Agent server failed to respond after starting. Please check the server logs.")
            return
    else:
        print("✅ Agent server running!")
    
    print("✅ Connected to agent server!")
    await _handle_allow_dir_command(os.getcwd(), agent_client)
    print("Type /help for commands.\n")
    
    try:
        while True:
            prompt = input("> ")
            if prompt.startswith("/"):
                if await _command(prompt, agent_client) == 1:
                    break
                continue

            # Run agent and display response
            await _entry(prompt, agent_client, stream=True)
    except KeyboardInterrupt:
        print("\n\nExiting...")
        return
    except EOFError:
        print("\nExiting...")
        return


def _run_sync():
    """Wrapper to run async code from sync context"""
    asyncio.run(_run())


if __name__ == "__main__":

    _run_sync()
    _exit()

