"""
GLOD Fullscreen TUI Editor

Provides a fullscreen text-based interface for GLOD using Rich.
Features:
- Message history display with scrolling
- Real-time response streaming
- Command palette with /help, /clear, /allow, /server commands
- Server status indicator
"""
import asyncio
from pathlib import Path

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.live import Live

from client import ClientSession, StreamEvent, EventType
from util import get_console


class GlodTUIEditor:
    """Fullscreen TUI editor for GLOD"""
    
    def __init__(self, project_root: Path = None):
        self.console = get_console()
        self.session = ClientSession(project_root=project_root)
        
        # Message history: list of (role, content) tuples
        # role: "user" or "agent"
        self.messages: list[tuple[str, str]] = []
        self.is_processing = False
        self.exit_requested = False
        self.streaming_response = ""  # Current streaming response being built
    
    async def run(self) -> None:
        """Main TUI loop"""
        try:
            # Initialize session
            if not await self.session.initialize():
                self.console.print("[red]✗ Failed to initialize agent server[/red]")
                return
            
            # Clear screen and show welcome
            self.console.clear()
            self.console.print(Panel("🔮 [bold cyan]GLOD AI Editor[/bold cyan] - Interactive Mode", style="cyan", padding=(0, 1)))
            self.console.print("[dim]Ready for input...[/dim]\n")
            
            while not self.exit_requested:
                # Get user input using Rich's Prompt
                try:
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
    
    def _render_screen(self) -> Layout:
        """Render the complete screen as a Layout"""
        # Build message display
        lines = []
        
        for role, content in self.messages:
            if role == "user":
                lines.append(f"[bold blue]You:[/bold blue]")
            else:
                lines.append(f"[bold green]Agent:[/bold green]")
            lines.append(f"  {content}")
            lines.append("")
        
        # Add streaming response if any
        if self.streaming_response:
            lines.append(f"[bold green]Agent:[/bold green]")
            lines.append(f"  {self.streaming_response}[yellow]▌[/yellow]")
        
        messages_content = "\n".join(lines) if lines else "[dim]No messages yet. Type a message to start![/dim]"
        
        # Header
        header_text = "🔮 GLOD AI Editor"
        if self.is_processing:
            header_text += " [yellow]⏳ Processing...[/yellow]"
        
        # Status bar
        server_status = "🟢 Server Running" if self.session.is_server_running() else "🔴 Server Offline"
        allowed_dirs_text = f"Allowed: {len(self.session.allowed_dirs)} dir(s) | Messages: {len(self.messages)}"
        
        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(Panel(header_text, style="cyan", padding=(0, 1)), name="header", size=3),
            Layout(Panel(f"{server_status}  •  {allowed_dirs_text}", style="dim white", padding=(0, 1)), name="status", size=3),
            Layout(Panel(messages_content, style="blue", padding=(0, 1), title="Messages"), name="messages"),
            Layout(Panel("[dim]/help • /clear • /allow <path> • /server [start|stop|restart|status] • /exit[/dim]", style="dim", padding=(0, 1)), name="footer", size=3),
        )
        
        return layout
    
    async def _send_message(self, message: str) -> None:
        """Send a message to the agent with streaming updates"""
        if not message.strip():
            return
        
        # Add user message to history and display it
        self.messages.append(("user", message))
        self.is_processing = True
        self.streaming_response = ""

        try:
            # Create Live display for streaming
            display = self._render_screen()
            with Live(display, console=self.console, refresh_per_second=20) as live:
                try:
                    # Stream response events
                    async for event in self.session.send_prompt_stream(message):
                        if event.type == EventType.CHUNK:
                            self.streaming_response += event.content
                            # Update display with streaming response
                            display = self._render_screen()
                            live.update(display)
                        
                        elif event.type == EventType.COMPLETE:
                            # Message history updated in agent client
                            pass
                        
                        elif event.type == EventType.TOOL_PHASE_START:
                            # Could show tool phase indicator if desired
                            pass
                        
                        elif event.type == EventType.TOOL_PHASE_END:
                            # Could hide tool phase indicator if desired
                            pass
                        
                        elif event.type == EventType.ERROR:
                            self.streaming_response += f"[red]Error: {event.content}[/red]"
                            display = self._render_screen()
                            live.update(display)
                    
                    # Add final response to messages
                    if self.streaming_response:
                        self.messages.append(("agent", self.streaming_response))
                    self.streaming_response = ""
                    # Final display update
                    display = self._render_screen()
                    live.update(display)
                
                finally:
                    self.is_processing = False
                    self.streaming_response = ""
        
        except Exception as e:
            self.messages.append(("agent", f"[red]Error:[/red] {str(e)}"))
        
        finally:
            self.is_processing = False
    
    def _format_status_message(self, message: str) -> str:
        """Format a status message with Rich markup.
        
        Converts plain text status messages into Rich markup:
        - ✓ → [green]✓[/green]
        - ℹ → [blue]ℹ[/blue]
        - Error: → [red]Error:[/red]
        """
        if message.startswith("✓"):
            return "[green]" + message + "[/green]"
        elif message.startswith("ℹ"):
            return "[blue]" + message + "[/blue]"
        elif message.startswith("Error:"):
            return "[red]" + message + "[/red]"
        elif message.startswith("Usage:"):
            return "[yellow]" + message + "[/yellow]"
        else:
            return message

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
            self.session.clear_history()
            self.messages.append(("agent", "[green]✓ Message history cleared[/green]"))
        
        elif command == "allow":
            if len(parts) > 1:
                result = await self.session.add_allowed_dir(parts[1])
                if result.get("status") == "ok":
                    self.messages.append(("agent", f"[green]✓ Added allowed directory: {result.get('path')}[/green]"))
                else:
                    self.messages.append(("agent", f"[red]Error: {result.get('message')}[/red]"))
            else:
                self.messages.append(("agent", "[yellow]Usage:[/yellow] /allow <directory_path>"))
        
        elif command == "server":
            await self._handle_server_command(parts[1] if len(parts) > 1 else None)
        
        else:
            self.messages.append(("agent", f"[red]Unknown command:[/red] /{command}"))
    
    async def _handle_server_command(self, subcommand: str = None) -> None:
        """Handle /server commands"""
        if subcommand is None:
            self.messages.append(("agent", "[yellow]Usage:[/yellow] /server [start|stop|restart|status]"))
            return
        
        subcommand = subcommand.lower()
        
        if subcommand == "start":
            if self.session.start_server():
                await asyncio.sleep(1)
                self.messages.append(("agent", "[green]✓ Agent server started[/green]"))
            else:
                self.messages.append(("agent", "[red]✗ Failed to start agent server[/red]"))
        
        elif subcommand == "stop":
            if self.session.stop_server():
                self.messages.append(("agent", "[green]✓ Agent server stopped[/green]"))
            else:
                self.messages.append(("agent", "[red]✗ Failed to stop agent server[/red]"))
        
        elif subcommand == "restart":
            if self.session.restart_server():
                await asyncio.sleep(1)
                try:
                    await self.session.sync_allowed_dirs()
                except Exception:
                    pass  # Best effort
                self.messages.append(("agent", "[green]✓ Agent server restarted[/green]"))
            else:
                self.messages.append(("agent", "[red]✗ Failed to restart agent server[/red]"))
        
        elif subcommand == "status":
            if self.session.is_server_running():
                pid = self.session.get_server_pid()
                self.messages.append(("agent", f"[green]✓ Agent server is running (PID: {pid})[/green]"))
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
        
