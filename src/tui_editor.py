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
from rich.console import ConsoleOptions, RenderResult

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
            self.console.clear()
    
    def _create_layout(self) -> Layout:
        """Create the main layout structure"""
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3),
        )
        layout["main"].split_column(
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

                    lines.append(f"    [dim]... ({len(content_lines) - 5} more lines)[/dim]")
            lines.append("")  # Blank line between messages
        
        return "\n".join(lines)
    
    def _render_input(self) -> str:
        """Render input area"""
        if self.input_buffer:
            return self.input_buffer
        return "[dim]Type your message here...[/dim]"
    
    def _render_status(self) -> Panel:
        """Render status bar"""
        server_status = "🟢 Server Running" if self.server_manager.is_running() else "🔴 Server Offline"
        allowed_dirs_text = f"Allowed dirs: {len(self.allowed_dirs)}"
        return Panel(f"{server_status} | {allowed_dirs_text}", style="dim", padding=(0, 1))
    
    def _render_footer(self) -> Panel:
        """Render footer with help text"""
        return Panel(
            "[dim]/help for commands • Ctrl+C to exit[/dim]",
            style="dim",
            padding=(0, 1),
        )
    
    async def _get_input_async(self) -> Optional[str]:
        """Get user input asynchronously using non-blocking stdin"""
        loop = asyncio.get_event_loop()
        
        # Read a single line of input
        try:
            char = await loop.run_in_executor(None, self._read_char_nonblocking)
            
            if char is None:
                return None
            
            if char == '\n':
                # User pressed enter - return the current buffer
                result = self.input_buffer
                self.input_buffer = ""
                return result if result else None
            elif char == '\x04':  # Ctrl+D
                # EOF/exit signal
                raise EOFError()
            elif char == '\x08' or char == '\x7f':  # Backspace
                # Delete last character
                if self.input_buffer:
                    self.input_buffer = self.input_buffer[:-1]
            elif char == '\x03':  # Ctrl+C
    async def _get_input_async(self) -> Optional[str]:
        """Get user input asynchronously using non-blocking stdin"""
        loop = asyncio.get_event_loop()
        
        # Read a single line of input
        try:
            char = await loop.run_in_executor(None, self._read_char_nonblocking)
            
            if char is None:
                return None
            
            # Handle special keys
            if char == '\r' or char == '\n':
                # User pressed enter - return the current buffer
                result = self.input_buffer
                self.input_buffer = ""
                return result if result else None
            elif char == '\x04':  # Ctrl+D
                # EOF/exit signal
                raise EOFError()
            elif char == '\x08' or char == '\x7f':  # Backspace
                # Delete last character
                if self.input_buffer:
                    self.input_buffer = self.input_buffer[:-1]
            elif char == '\x03':  # Ctrl+C
                raise KeyboardInterrupt()
            elif ord(char) >= 32:  # Printable ASCII characters
                # Add to input buffer
                self.input_buffer += char
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

            # Try to read one byte
            char = os.read(sys.stdin.fileno(), 1)
            if char:
                return char.decode('utf-8', errors='ignore')
            return None
        except (OSError, IOError):
            # Would block or other I/O error
            return None

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
            
