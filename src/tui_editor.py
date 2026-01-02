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
import os
import sys
from typing import Optional
from pathlib import Path

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.table import Table
from rich.console import ConsoleOptions, RenderResult

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
        self.input_lines: list[str] = []
        self.is_processing = False
        self.exit_requested = False
        
    async def run(self) -> None:
        """Main TUI loop"""
        try:
            # Clear screen and show welcome
            self.console.clear()
            self.console.print(Panel("🔮 [bold cyan]GLOD AI Editor[/bold cyan] - Fullscreen Mode", style="cyan", padding=(0, 1)))
            self.console.print("[dim]Loading...[/dim]\n")
            
            # Create layout
            layout = self._create_layout()
            
            with Live(layout, refresh_per_second=2, screen=True) as live:
                while not self.exit_requested:
                    # Update layout
                    self._update_layout(layout)
                    
                    # Get user input (non-blocking in TUI context)
                    user_input = await self._get_input()
                    
                    if user_input is None:  # Exit signal
                        break
                    
                    if user_input.strip():
                        if user_input.startswith("/"):
                            await self._handle_command(user_input)
                        else:
                            await self._send_message(user_input)
                    
                    self.input_lines = []
        
        except KeyboardInterrupt:
            pass
        finally:
            self.console.clear()
    
    def _create_layout(self) -> Layout:
        """Create the TUI layout"""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="messages", ratio=1),
            Layout(name="status", size=1),
            Layout(name="input", size=7),
            Layout(name="footer", size=1),
        )
        return layout
    
    def _update_layout(self, layout: Layout) -> None:
        """Update layout with current state"""
        # Header
        header_text = "🔮 [bold cyan]GLOD AI Editor[/bold cyan]"
        if self.is_processing:
            header_text += " [bold yellow]⏳ Processing...[/bold yellow]"
        layout["header"].update(Panel(header_text, style="cyan", padding=(0, 1)))
        
        # Messages panel
        messages_text = self._render_messages()
        layout["messages"].update(Panel(messages_text, style="blue", border_style="blue"))
        
        # Status bar
        status = self._render_status()
        layout["status"].update(status)
        
        # Input panel
        input_panel = self._render_input()
        layout["input"].update(Panel(input_panel, title="[bold yellow]Input (Ctrl+D to submit)[/bold yellow]", style="yellow", padding=(0, 1)))
        
        # Footer
        footer = self._render_footer()
        layout["footer"].update(footer)
    
    def _render_messages(self) -> str:
        """Render message history"""
        if not self.messages:
            return "[dim]No messages yet. Type a message to begin![/dim]"
        
        # Show last 20 messages to avoid overwhelming display
        visible_messages = self.messages[-20:]
        
        lines = []
        for role, content in visible_messages:
            if role == "user":
                # Show user message - truncate if very long
                content_lines = content.split("\n")
                for i, line in enumerate(content_lines[:3]):  # Show first 3 lines
                    if i == 0:
                        lines.append(f"[bold yellow]You:[/bold yellow] {line[:80]}")
                    else:
                        lines.append(f"    {line[:80]}")
                if len(content_lines) > 3:
                    lines.append(f"    [dim]... ({len(content_lines) - 3} more lines)[/dim]")
            else:
                # Agent response - show first few lines
    
    async def _get_input(self) -> Optional[str]:
        """Get user input (reads until EOF or complete message)"""
        try:
            # Use a simple prompt that doesn't interfere with Live display
            loop = asyncio.get_event_loop()
            
            # Read line by line until we get an empty line or EOF
            # This is simplified - just get one line at a time for now
            line = await loop.run_in_executor(
                None,
                lambda: self._read_line_safe()
            )
            
            if line is None:
                return None
            
            # If it's a command, return immediately
            if line.startswith("/"):
                return line
            
            # Otherwise, add to input buffer and wait for more
            self.input_lines.append(line)
            
            # For multi-line input, keep reading until empty line
            # or just return after each line for now
            if self.input_lines:
                return "\n".join(self.input_lines)
            
            return None
        
        except EOFError:
            return None
    
    def _read_line_safe(self) -> Optional[str]:
        """Safely read a line from stdin without interfering with Live display"""
        try:
            # Simple non-blocking read
            return input()
        except EOFError:
            return None
        except KeyboardInterrupt:
            raise
    
    async def _send_message(self, prompt: str) -> None:
        """Send a message to the agent"""
        # Add user message to history
        self.messages.append(("user", prompt))
        self.is_processing = True
        
        try:
            # Set up event handlers for streaming
            response_buffer = []
            
            def on_chunk(content: str):
                response_buffer.append(content)
            
            # Temporarily replace event handler
            old_handler = getattr(self.agent_client, 'on_chunk', None)
            self.agent_client.on_chunk = on_chunk
            
            # Get response from agent
            await self.agent_client.run_stream(prompt)
            
            # Restore old handler
            if old_handler:
                self.agent_client.on_chunk = old_handler
            
            # Add agent response to history
            full_response = "".join(response_buffer)
            if full_response:
                self.messages.append(("agent", full_response))
        
        except Exception as e:
            self.messages.append(("agent", f"[red]Error:[/red] {str(e)}"))
        
        finally:
            self.is_processing = False
    
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

