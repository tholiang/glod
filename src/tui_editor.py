"""

GLOD Simple CLI Editor

Provides a simple text-based interface for GLOD using Rich.

Features:

- Sequential output (no panels or layouts)

- Real-time response streaming

- Command palette with /help, /clear, /allow, /server commands
"""
import asyncio
from pathlib import Path

from rich.console import Console

from client import ClientSession, StreamEvent, EventType

from util import get_console

class GlodTUIEditor:
    def __init__(self, project_root: Path | None = None):
        self.console = get_console()
        self.session = ClientSession(project_root=project_root)
        
        # Message history: list of (role, content) tuples
        # role: "user" or "agent"
        self.messages: list[tuple[str, str]] = []
        self.is_processing = False
        self.exit_requested = False

    async def run(self) -> None:
        """Main CLI loop"""
        try:
            # Initialize session
            if not await self.session.initialize():
                self.console.print("[red]✗ Failed to initialize agent server[/red]")
                return
            
            # Show welcome
            self.console.print("[cyan]🔮 GLOD AI Editor[/cyan] - Ready for input\n")
            
            while not self.exit_requested:
                try:
                    user_input = self.console.input("[bold green]You:[/bold green] ").strip()
                    
                    if not user_input:
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
            self.console.print(f"[red]Error: {str(e)}[/red]")
        finally:
            pass

    async def _send_message(self, message: str) -> None:
        """Send a message to the agent with streaming updates"""
        if not message.strip():
            return
        
        # Add user message to history
        self.messages.append(("user", message))
        self.is_processing = True
        streaming_response = ""

        try:
            self.console.print()  # Blank line before response
            self.console.print("[bold green]Agent:[/bold green]", end=" ")
            
            # Stream response events
            async for event in self.session.send_prompt_stream(message):
                if event.type == EventType.CHUNK:
                    self.console.print(event.content, end="", highlight=False)
                    streaming_response += event.content
                
                elif event.type == EventType.TOOL_CALL:
                    tool_msg = f"[cyan]→ {event.content}[/cyan]"
                    self.console.print(f"\n{tool_msg}", end="")
                
                elif event.type == EventType.TOOL_RESULT:
                    result_msg = f" [green]✓[/green]"
                    self.console.print(result_msg, end="")
                
                elif event.type == EventType.TOOL_PHASE_START:
                    self.console.print("\n[yellow]⚙️  Tool phase started[/yellow]")
                
                elif event.type == EventType.TOOL_PHASE_END:
                    self.console.print("[yellow]⚙️  Tool phase complete[/yellow]")
                
                elif event.type == EventType.COMPLETE:
                    pass
                
                elif event.type == EventType.ERROR:
                    error_msg = f"[red]Error: {event.content}[/red]"
                    self.console.print(f"\n{error_msg}", end="")
            
            # Add final response to messages
            if streaming_response:
                self.messages.append(("agent", streaming_response))
            
            self.console.print("\n")  # Blank line after response
        
        except Exception as e:
            error_msg = f"[red]Error:[/red] {str(e)}"
            self.messages.append(("agent", str(e)))
            self.console.print(f"\n{error_msg}\n")
        
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
            self.session.clear_history()
            self.console.print("[green]✓ Message history cleared[/green]\n")
        
        elif command == "allow":
            if len(parts) > 1:
                result = await self.session.add_allowed_dir(parts[1])
                if result.get("status") == "ok":
                    self.console.print(f"[green]✓ Added allowed directory: {result.get('path')}[/green]\n")
                else:
                    self.console.print(f"[red]Error: {result.get('message')}[/red]\n")
            else:
                self.console.print("[yellow]Usage:[/yellow] /allow <directory_path>\n")
        
        elif command == "server":
            await self._handle_server_command(parts[1] if len(parts) > 1 else None)
        
        elif command == "status":
            await self._show_status()
        
        else:
            self.console.print(f"[red]Unknown command:[/red] /{command}\n")
    
    async def _handle_server_command(self, subcommand: str | None = None) -> None:
        """Handle /server commands"""
        if subcommand is None:
            self.console.print("[yellow]Usage:[/yellow] /server [start|stop|restart|status]\n")
            return
        
        subcommand = subcommand.lower()
        
        if subcommand == "start":
            if self.session.start_server():
                await asyncio.sleep(1)
                self.console.print("[green]✓ Agent server started[/green]\n")
            else:
                self.console.print("[red]✗ Failed to start agent server[/red]\n")
        
        elif subcommand == "stop":
            if self.session.stop_server():
                self.console.print("[green]✓ Agent server stopped[/green]\n")
            else:
                self.console.print("[red]✗ Failed to stop agent server[/red]\n")
        
        elif subcommand == "restart":
            if self.session.restart_server():
                await asyncio.sleep(1)
                try:
                    await self.session.sync_allowed_dirs()
                except Exception:
                    pass  # Best effort
                self.console.print("[green]✓ Agent server restarted[/green]\n")
            else:
                self.console.print("[red]✗ Failed to restart agent server[/red]\n")
        
        elif subcommand == "status":
            await self._show_status()
        
         else:
             self.console.print(f"[red]Unknown server command:[/red] {subcommand}\n")
     
     async def _show_status(self) -> None:
         """Display server and session status"""
         server_status = "🟢 Running" if self.session.is_server_running() else "🔴 Offline"
         pid = self.session.get_server_pid() if self.session.is_server_running() else None
         
         self.console.print(f"[cyan]Server:[/cyan] {server_status}" + (f" (PID: {pid})" if pid else "") + "\n")
         self.console.print(f"[cyan]Allowed directories:[/cyan] {len(self.session.allowed_dirs)}\n")
         self.console.print(f"[cyan]Messages in history:[/cyan] {len(self.messages)}\n")
     
     async def _show_help(self) -> None:
         """Display help"""
         help_text = """[bold cyan]Available Commands:[/bold cyan]

[yellow]/allow <path>[/yellow]        Add a directory to allowed file access paths
[yellow]/clear[/yellow]              Clear message history
[yellow]/server start[/yellow]       Start the agent server
[yellow]/server stop[/yellow]        Stop the agent server
[yellow]/server restart[/yellow]     Restart the agent server
[yellow]/server status[/yellow]      Check agent server status
[yellow]/status[/yellow]             Show server and session status
[yellow]/help[/yellow]               Show this help message
[yellow]/exit[/yellow]               Exit GLOD
"""
         self.console.print(help_text)

        
