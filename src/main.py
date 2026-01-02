"""
GLOD CLI - Beautiful AI Code Editor Interface

Client for interacting with the agent via HTTP RPC.
- Manages message history
- Handles user interaction with rich formatting
- Communicates with agent via HTTP (with streaming support)
- Can start/stop/restart the agent server
- Maintains a persistent list of allowed directories
"""
import os
import sys
from pathlib import Path
import asyncio
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.syntax import Syntax
from rich.live import Live
from rich.align import Align
from rich import print as rprint

from client_agent import AgentClient
from server_manager import ServerManager

# Initialize Rich console and Typer app
console = Console()
app = typer.Typer(
    name="glod",
    help="AI Code Editor - Chat with Claude about your codebase",
    rich_markup_mode="rich",
    no_args_is_help=False,
)

# Global instances
server_manager = ServerManager(project_root=Path(__file__).parent.parent)
agent_client: Optional[AgentClient] = None
allowed_dirs: list[str] = []

# Track if we're in a tool call/response phase
_in_tool_phase = False
_tool_phase_buffer = []


def print_welcome():
    """Display welcome message"""
    welcome_text = Text.from_markup(
        "[bold cyan]GLOD[/bold cyan] - [yellow]AI Code Editor[/yellow]"
    )
    console.print(
        Panel(
            welcome_text,
            expand=False,
            border_style="cyan",
            padding=(1, 2),
        )
    )


def print_success(message: str):
    """Print success message"""
    console.print(f"[green]✓[/green] {message}")


def print_error(message: str):
    """Print error message"""
    console.print(f"[red]✗[/red] {message}")


def print_info(message: str):
    """Print info message"""
    console.print(f"[blue]ℹ[/blue] {message}")
def print_response_header(title: str = "Agent Response"):
    """Print a nice header for agent response"""
    console.print()
    console.print(Panel.fit(f"[bold cyan]{title}[/bold cyan]", border_style="cyan"))


def print_response_footer():
    """Print a footer after agent response"""
    console.print()


async def _entry(prompt: str, stream: bool = True) -> None:
    """
    Send request to agent and display response.
    
    Args:
        prompt: The user's prompt
        stream: Whether to use streaming response (default True)
    """
    if not agent_client:
        print_error("Agent client not initialized")
        return
    
    # Set up event handlers for better formatting
    tool_buffer = []
    
    def on_tool_phase_start():
        """Called when entering tool call/result phase"""
        console.print()
        console.print(Panel("🔧 [bold yellow]Tool Calls[/bold yellow]", border_style="yellow", padding=(0, 1)))
    
    def on_tool_call(content: str):
        """Handle tool call event"""
        # Parse the tool call to extract tool name and params
        # For now, just print it formatted nicely
        lines = content.strip().split('\n')
        if lines:
            first_line = lines[0]
            # Try to extract tool name (typically format: "Calling tool: <name>" or similar)
            if 'Calling' in first_line or 'tool' in first_line.lower():
                console.print(f"  [yellow]→[/yellow] {first_line}")
                for line in lines[1:]:
                    console.print(f"    {line}")
            else:
                console.print(f"  [yellow]→[/yellow] {content}")
        tool_buffer.append(content)
    
    def on_tool_result(content: str):
        """Handle tool result event"""
        # Format as a nice result box
        lines = content.strip().split('\n')
        if len(lines) > 1:
            console.print(f"  [blue]←[/blue] [dim]{lines[0]}[/dim]")
            for line in lines[1:]:
                console.print(f"      {line}")
        else:
            console.print(f"  [blue]←[/blue] {content}")
        tool_buffer.append(content)
    
    def on_tool_phase_end():
        """Called when exiting tool call/result phase"""
        console.print()
        console.print(Panel("📝 [bold cyan]Response[/bold cyan]", border_style="cyan", padding=(0, 1)))
    
    def on_chunk(content: str):
        """Handle response chunk - output directly"""
        print(content, end="", flush=True)
    
    # Register handlers
    agent_client.on_tool_phase_start = on_tool_phase_start
    agent_client.on_tool_call = on_tool_call
    agent_client.on_tool_result = on_tool_result
    agent_client.on_tool_phase_end = on_tool_phase_end
    agent_client.on_chunk = on_chunk
    
    if stream:
        await agent_client.run_stream(prompt)
    else:
        await agent_client.run(prompt)
    
    print_response_footer()
        else:
            print_error(f"Failed to add directory: {response}")
    except Exception as e:
        print_error(f"Failed to add allowed directory: {str(e)}")


async def _sync_allowed_dirs() -> None:
    """Sync allowed directories with server"""
    for dir_path in allowed_dirs:
        await _handle_allow_dir_command(dir_path)


async def _handle_server_command(subcommand: Optional[str]) -> None:
    """Handle /server commands"""
    if subcommand is None:
        print_info("Usage: /server [start|stop|restart|status]")
        return

    subcommand = subcommand.lower()
    
    if subcommand == "start":
        print_info("Starting agent server...")
        server_manager.start()
        await asyncio.sleep(1)
        print_success("Agent server started")
    
    elif subcommand == "stop":
        print_info("Stopping agent server...")
        server_manager.stop()
        print_success("Agent server stopped")
    
    elif subcommand == "restart":
        print_info("Restarting agent server...")
        server_manager.restart()
        await asyncio.sleep(1)
        await _sync_allowed_dirs()
        print_success("Agent server restarted")
    
    elif subcommand == "status":
        if server_manager.is_running():
            pid = server_manager.get_pid()
            print_success(f"Agent server is running (PID: {pid})")
        else:
            print_error("Agent server is not running")
    
    else:
        print_error(f"Unknown server command: {subcommand}")
        print_info("Usage: /server [start|stop|restart|status]")


def print_help():
    """Display help with all available commands"""
    help_table = Table(title="Available Commands", show_header=True, header_style="bold cyan")
    help_table.add_column("Command", style="yellow", width=25)
    help_table.add_column("Description", width=50)
    
    help_table.add_row("/allow <path>", "Add a directory to allowed file access paths")
    help_table.add_row("/clear", "Clear message history with the agent")
    help_table.add_row("/server start", "Start the agent server")
    help_table.add_row("/server stop", "Stop the agent server")
    help_table.add_row("/server restart", "Restart the agent server")
    help_table.add_row("/server status", "Check agent server status")
    help_table.add_row("/help", "Show this help message")
    help_table.add_row("/exit", "Exit the program")
    
    console.print()
    console.print(help_table)
    console.print()


async def _command(prompt: str) -> int:
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
            await _handle_allow_dir_command(parts[1])
        else:
            print_error("Usage: /allow <directory_path>")
    
    elif command == "clear":
        if agent_client:
            agent_client.clear_history()
            print_success("Message history cleared")
    
    elif command == "server":
        await _handle_server_command(parts[1] if len(parts) > 1 else None)
    
    elif command == "help":
        print_help()
    
    else:
        print_error(f"Unknown command: /{command}")
    
    return 0


async def _run_interactive():
    """Main interactive loop"""
    global agent_client, allowed_dirs
    
    # Initialize client
    agent_client = AgentClient()
    allowed_dirs = [os.getcwd()]
    
    print_welcome()
    console.print()
    
    # Check and start server if needed
    if not await agent_client.health_check():
        print_error("Agent server is not running")
        print_info("Starting agent server automatically...\n")
        
        if not server_manager.start():
            print_error("Failed to start agent server. Exiting.")
            return
        
        await asyncio.sleep(1)
        
        if not await agent_client.health_check():
            print_error("Agent server failed to respond after starting")
            return
    
    print_success("Agent server is running")
    print_success("Connected to agent server!")
    await _sync_allowed_dirs()
    print_info("Type [yellow]/help[/yellow] for commands\n")
    
    # Prompt style
    prompt_style = "[bold cyan]>[/bold cyan] "
    
    try:
        while True:
            try:
                prompt = console.input(prompt_style)
            except EOFError:
                print_info("End of input reached")
                break
            
            if not prompt.strip():
                continue
            
            if prompt.startswith("/"):
                if await _command(prompt) == 1:
                    break
                continue
            
            # Run agent and display response
            await _entry(prompt, stream=True)
    
    except KeyboardInterrupt:
        console.print()
        print_info("Exiting...")
        return


def _run_sync():
    """Wrapper to run async code from sync context"""
    try:
        asyncio.run(_run_interactive())
    except KeyboardInterrupt:
        pass
    finally:
        server_manager.stop()
        console.print()


if __name__ == "__main__":
    _run_sync()

