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
import fcntl
from typing import Optional
from pathlib import Path

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.table import Table

from client_agent import AgentClient
from server_manager import ServerManager
from client_lib import (
    print_success,
    print_error,
    print_info,
    get_console,
)

try:
    import tty
    import termios
except ImportError:
    tty = None
    termios = None


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
        self.input_buffer: str = ""  # Current input being typed
        self.is_processing = False
        self.exit_requested = False
    
    async def run(self) -> None:
        """Main TUI loop"""
        # Save original terminal settings
        original_settings = None
        if tty and termios:
            try:
                original_settings = termios.tcgetattr(sys.stdin)
                tty.setraw(sys.stdin.fileno())
            except:
                pass
        
        try:
            # Clear screen and show welcome
            self.console.clear()
            self.console.print(Panel("🔮 [bold cyan]GLOD AI Editor[/bold cyan] - Fullscreen Mode", style="cyan", padding=(0, 1)))
            self.console.print("[dim]Loading...[/dim]\n")
            
            # Create layout
            layout = self._create_layout()
            
            with Live(layout, refresh_per_second=4, screen=True) as live:
                while not self.exit_requested:
                    # Update layout
                    self._update_layout(layout)
                    live.update(layout)
                    
                    # Get user input (non-blocking)
                    try:
                        user_input = await asyncio.wait_for(
                            self._get_input_async(), 
                            timeout=0.25
                        )
                        
                        if user_input is not None:
                            if user_input.startswith("/"):
                                await self._handle_command(user_input)
                            else:
                                await self._send_message(user_input)
                            self.input_buffer = ""
                    except asyncio.TimeoutError:
                        # No input available, keep updating display
                        pass
                    except EOFError:
                        break
        
        except KeyboardInterrupt:
            pass
        finally:
            # Restore original terminal settings
            if original_settings and tty and termios:
                try:
                    termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, original_settings)
                except:
                    pass
            self.console.clear()
    
    def _create_layout(self) -> Layout:
        """Create the main layout structure with responsive sizing"""
        layout = Layout()
        # Split vertically: header (fixed 3), main (flex), footer (fixed 3)
        layout.split_vertical(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3),
        )
        # Split main area: messages (60% flex), input_section (40% flex)
        layout["main"].split_row(
            Layout(name="messages", ratio=3),
            Layout(name="input_section", ratio=1),
        )
        # Split input section: status (fixed 2) above input (flex)
        layout["input_section"].split_vertical(
            Layout(name="status", size=2),
            Layout(name="input"),
        )
        return layout

    def _update_layout(self, layout: Layout) -> None:
        """Update layout contents"""
        # Header
        header_text = "🔮 GLOD AI Editor"
        if self.is_processing:
            header_text += " [yellow]⏳ Processing...[/yellow]"
        layout["header"].update(
            Panel(header_text, style="cyan", padding=(0, 1), expand=False)
        )
        
        # Messages
        messages_panel = Panel(
            self._render_messages(), 
            style="blue", 
            padding=(0, 1),
            title="Messages",
            expand=True,
        )
        layout["messages"].update(messages_panel)
        
        # Status
        layout["status"].update(self._render_status())
        
        # Input
        input_panel = Panel(
            self._render_input(), 
            style="green", 
            padding=(0, 1), 
            title="Input",
            expand=True,
        )
        
        # Footer
        layout["footer"].update(self._render_footer())

        layout["input"].update(input_panel)
    def _render_messages(self) -> str:
        """Render message history with word wrapping"""
        lines = []
        
        # Show last 20 messages
        for role, content in self.messages[-20:]:
            if role == "user":
                lines.append(f"[bold blue]You:[/bold blue]")
                lines.append(f"  {content}")
            else:
                lines.append(f"[bold green]Agent:[/bold green]")
                lines.append(f"  {content}")
            
            lines.append("")  # Blank line between messages
        
        return "\n".join(lines) if lines else "[dim]No messages yet. Type a message to start![/dim]"
    def _render_input(self) -> str:
        """Render input area"""
        if self.input_buffer:
            return self.input_buffer
        return "[dim]Type your message here...[/dim]"
    
    def _render_status(self) -> Panel:
        """Render status bar"""
        server_status = "🟢 Server Running" if self.server_manager.is_running() else "🔴 Server Offline"
        allowed_dirs_text = f"Allowed: {len(self.allowed_dirs)} dir(s) | Messages: {len(self.messages)}"
        return Panel(
            f"{server_status}  •  {allowed_dirs_text}", 
            style="dim white", 
            padding=(0, 1),
            expand=False,
        )
    
    def _render_footer(self) -> Panel:
        """Render footer with help text"""
        return Panel(
            "[dim]/help • /clear • /allow <path> • /server [start|stop|restart|status] • /exit[/dim]",
            style="dim",
            padding=(0, 1),
            expand=False,
        )


    
    def _read_char_nonblocking(self) -> Optional[str]:
        """Read a single character without blocking"""
        try:
            # Set O_NONBLOCK flag if not already set
            flags = fcntl.fcntl(sys.stdin.fileno(), fcntl.F_GETFL)
            if not (flags & os.O_NONBLOCK):
                fcntl.fcntl(sys.stdin.fileno(), fcntl.F_SETFL, flags | os.O_NONBLOCK)
            
            # Try to read one byte
            char = os.read(sys.stdin.fileno(), 1)
            if char:
                return char.decode('utf-8', errors='ignore')
            return None
        except (OSError, IOError):
            # Would block or other I/O error
            return None
    
    async def _send_message(self, message: str) -> None:
        """Send a message to the agent"""
        if not message.strip():
            return
        
        # Add user message to history
        self.messages.append(("user", message))
        self.is_processing = True
        
        try:
            # Format message history for agent
            history_text = "\n".join([
                f"{'User' if role == 'user' else 'Agent'}: {content}"
                for role, content in self.messages[:-1]  # Exclude the current message
            ])
            
            # Stream response
            full_response = ""
            
            async for chunk in self.agent_client.stream_run(
                prompt=message,
                message_history=history_text
            ):
                full_response += chunk
                # Update the display with streaming response
                if self.messages and self.messages[-1][0] == "agent":
                    self.messages[-1] = ("agent", full_response)
                else:
                    self.messages.append(("agent", full_response))
            
            # Ensure the final response is stored
            if full_response and (not self.messages or self.messages[-1][0] != "agent"):
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
