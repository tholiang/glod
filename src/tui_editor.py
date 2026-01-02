"""
GLOD Fullscreen TUI Editor

Provides a fullscreen text-based interface for GLOD using Rich.
Features:
- Message history display with scrolling
- Multi-line input area
- Real-time response streaming
- Command palette with /help, /clear, /allow, /server commands
- Server status indicator
"""
import asyncio
from typing import Optional
from pathlib import Path

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.table import Table
from rich.prompt import Prompt

from client_agent import AgentClient
from server_manager import ServerManager
from client_lib import (
    print_success,
    print_error,
    print_info,
    get_console,
)


class GlodTUIEditor:
    """Fullscreen TUI editor for GLOD"""
    
    def __init__(
        self, 
        agent_client: AgentClient,
        server_manager: ServerManager,
        allowed_dirs: list[str],
    ):
        self.console = get_console()
        self.agent_client = agent_client
        self.server_manager = server_manager
        self.allowed_dirs = allowed_dirs
        
        # Message history: list of (role, content) tuples
        # role: "user" or "agent"
        self.messages: list[tuple[str, str]] = []
        self.is_processing = False
        self.exit_requested = False
        self.streaming_response = ""  # Current streaming response being built
    
    async def run(self) -> None:
        """Main TUI loop"""
        try:
            # Clear screen and show welcome
            self.console.clear()
            self.console.print(Panel("🔮 [bold cyan]GLOD AI Editor[/bold cyan] - Interactive Mode", style="cyan", padding=(0, 1)))
            self.console.print("[dim]Ready for input...[/dim]\n")
            
            while not self.exit_requested:
                # Display current state with Live updating
                self._render_display()
                
                # Get user input using Rich's Prompt
                try:
                    # Create a custom prompt that doesn't add extra output
                    user_input = self.console.input("\n[bold green]You:[/bold green] ")
                    
                    if not user_input.strip():
                        continue
                    
                    if user_input.startswith("/"):
                        await self._handle_command(user_input)
                    else:
                        await self._send_message(user_input)
                
                except EOFError:
                    break
                except KeyboardInterrupt:
                    self.console.print("\n[yellow]^C[/yellow]")
                    break
        
        except Exception as e:
            self.console.print("[red]Error in TUI loop: [/red]"+str(e))
        finally:
            self.console.clear()
    
    def _render_display(self) -> None:
        """Render the current display state"""
        self.console.clear()
        
        # Header
        header_text = "🔮 GLOD AI Editor"
        if self.is_processing:
            header_text += " [yellow]⏳ Processing...[/yellow]"
        self.console.print(Panel(header_text, style="cyan", padding=(0, 1)))
        
        # Status bar
        server_status = "🟢 Server Running" if self.server_manager.is_running() else "🔴 Server Offline"
        allowed_dirs_text = f"Allowed: {len(self.allowed_dirs)} dir(s) | Messages: {len(self.messages)}"
        self.console.print(Panel(
            f"{server_status}  •  {allowed_dirs_text}",
            style="dim white",
            padding=(0, 1),
        ))
        
        # Messages
        self.console.print(Panel(
            self._render_messages(),
            style="blue",
            padding=(0, 1),
            title="Messages",
        ))
        
        # Footer with help
        self.console.print(Panel(
            "[dim]/help • /clear • /allow <path> • /server [start|stop|restart|status] • /exit[/dim]",
            style="dim",
            padding=(0, 1),
        ))
    
    def _render_messages(self) -> str:
        """Render message history with word wrapping"""
        lines = []
        
        # Show all messages
        for role, content in self.messages:
            if role == "user":
    async def _send_message(self, message: str) -> None:
        """Send a message to the agent with streaming updates"""
        if not message.strip():
            return
        
        # Add user message to history
        self.messages.append(("user", message))
        self.is_processing = True
        self.streaming_response = ""
        
        try:
            # Format message history for agent
            history_text = "\n".join([
                f"{'User' if role == 'user' else 'Agent'}: {content}"
                for role, content in self.messages[:-1]  # Exclude the current message
            ])
            
            # Create initial renderable for Live display
            initial_renderable = self._render_live_display()
            
            # Use Live context manager for streaming updates
            with Live(initial_renderable, console=self.console, refresh_per_second=20) as live:
                try:
                    # Stream response
                    async for chunk in self.agent_client.stream_run(
                        prompt=message,
                        message_history=history_text
                    ):
                        self.streaming_response += chunk
                        # Update display with streaming response
                        display_content = self._render_live_display()
                        live.update(display_content)
                    
                    # Add final response to messages
                    if self.streaming_response:
                        self.messages.append(("agent", self.streaming_response))
                
                finally:
                    # Stop processing
                    self.is_processing = False
                    self.streaming_response = ""
        
        except Exception as e:
            self.messages.append(("agent", f"[red]Error:[/red] {str(e)}"))
        
        finally:
            self.is_processing = False
            self.streaming_response = ""

            self.messages.append(("agent", f"[red]Error:[/red] {str(e)}"))
        
        finally:
            self.is_processing = False
            self.streaming_response = ""
    
    def _render_live_display(self) -> Panel:
        """Render display content for Live updates"""
        # Header
        header_text = "🔮 GLOD AI Editor"
        if self.is_processing:
            header_text += " [yellow]⏳ Processing...[/yellow]"
        
        # Status bar
        server_status = "🟢 Server Running" if self.server_manager.is_running() else "🔴 Server Offline"
        allowed_dirs_text = f"Allowed: {len(self.allowed_dirs)} dir(s) | Messages: {len(self.messages)}"
        
        # Build complete message display including streaming response
        lines = []
        
        for role, content in self.messages:
            if role == "user":
                lines.append(f"[bold blue]You:[/bold blue]")
                lines.append(f"  {content}")
            else:
                lines.append(f"[bold green]Agent:[/bold green]")
                lines.append(f"  {content}")
            
            lines.append("")
        
        # Add streaming response if any
        if self.streaming_response:
            lines.append(f"[bold green]Agent:[/bold green]")
            lines.append(f"  {self.streaming_response}")
        
        messages_content = "\n".join(lines) if lines else "[dim]No messages yet. Type a message to start![/dim]"
        
        # Return the complete display as a Panel
        return Panel(
            messages_content,
            style="blue",
            padding=(0, 1),
            title="Messages",
        )
    
    async def _handle_command(self, command_str: str) -> None:
        """Handle / commands"""
        stripped = command_str.strip()[1:].lower()
        parts = stripped.split(maxsplit=1)
        command = parts[0]
        
        if command == "exit":
            self.exit_requested = True
            return
        
        elif command == "help":
            await self._show_help()
        
        elif command == "clear":
            self.messages.clear()
            self.agent_client.clear_history()
            self.messages.append(("agent", "[green]✓ Message history cleared[/green]"))
        
        elif command == "allow":
            if len(parts) > 1:
                await self._handle_allow_dir(parts[1])
            else:
                self.messages.append(("agent", "[red]Usage:[/red] /allow <directory_path>"))
        
        elif command == "server":
            await self._handle_server_command(parts[1] if len(parts) > 1 else None)
        
        else:
            self.messages.append(("agent", f"[red]Unknown command:[/red] /{command}"))
    
    async def _handle_allow_dir(self, dir_path: str) -> None:
        """Handle /allow command"""
        import os
        abs_path = os.path.abspath(dir_path)
        
        if not os.path.isdir(abs_path):
            self.messages.append(("agent", f"[red]Directory does not exist:[/red] {abs_path}"))
            return
        
        if abs_path not in self.allowed_dirs:
            self.allowed_dirs.append(abs_path)
        
        try:
            await self.agent_client.add_allowed_dir(abs_path)
            self.messages.append(("agent", f"[green]✓ Added allowed directory:[/green] {abs_path}"))
        except Exception as e:
            self.messages.append(("agent", f"[red]Failed to add directory:[/red] {str(e)}"))
    
    async def _handle_server_command(self, subcommand: Optional[str]) -> None:
        """Handle /server commands"""
        if subcommand is None:
            self.messages.append(("agent", "[yellow]Usage:[/yellow] /server [start|stop|restart|status]"))
            return
        
        subcommand = subcommand.lower()
        
        if subcommand == "start":
            self.server_manager.start()
            await asyncio.sleep(1)
            self.messages.append(("agent", "[green]✓ Agent server started[/green]"))
        
        elif subcommand == "stop":
            self.server_manager.stop()
            self.messages.append(("agent", "[green]✓ Agent server stopped[/green]"))
        
        elif subcommand == "restart":
            self.server_manager.restart()
            await asyncio.sleep(1)
            self.messages.append(("agent", "[green]✓ Agent server restarted[/green]"))
        
        elif subcommand == "status":
            if self.server_manager.is_running():
                pid = self.server_manager.get_pid()
                self.messages.append(("agent", f"[green]✓ Agent server is running[/green] (PID: {pid})"))
            else:
                self.messages.append(("agent", "[red]✗ Agent server is not running[/red]"))
        
        else:
            self.messages.append(("agent", f"[red]Unknown server command:[/red] {subcommand}"))
    
    async def _show_help(self) -> None:
        """Display help in message history"""
        help_text = """[bold cyan]Available Commands:[/bold cyan]
[yellow]/allow <path>[/yellow]        Add a directory to allowed file access paths
[yellow]/clear[/yellow]              Clear message history
[yellow]/server start[/yellow]       Start the agent server
[yellow]/server stop[/yellow]        Stop the agent server
[yellow]/server restart[/yellow]     Restart the agent server
[yellow]/server status[/yellow]      Check agent server status
[yellow]/help[/yellow]               Show this help message
[yellow]/exit[/yellow]               Exit GLOD"""
        
        self.messages.append(("agent", help_text))

