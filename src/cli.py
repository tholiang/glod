"""
GLOD CLI - Beautiful AI Code Editor Interface

Handles all user interaction and output presentation.
Delegates actual operations to ClientSession.
"""
import os
import asyncio
from pathlib import Path
from typing import Optional

from client import ClientSession, StreamEvent, EventType
from util import (
    print_welcome, print_success, print_error, print_info,
    print_response_footer, print_help, get_console
)
from rich.panel import Panel

console = get_console()


class CLI:
    """Command-line interface for GLOD"""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize CLI with a client session"""
        if project_root is None:
            project_root = Path(os.getcwd())
        
        self.session = ClientSession(project_root=project_root)
    
    async def initialize(self) -> bool:
        """Initialize the CLI and ensure server is running"""
        if not await self.session.initialize():
            print_error("Agent server is not running")
            print_info("Starting agent server automatically...\n")
            
            # Note: server start is already attempted in session.initialize()
            # This shouldn't be reached, but kept for clarity
            return False
        
        print_success("Agent server is running")
        print_success("Connected to agent server!")
        print_info("Type [yellow]/help[/yellow] for commands\n")
        
        return True
    
    async def handle_prompt(self, prompt: str, stream: bool = True) -> None:
        """
        Handle a user prompt and display the response.
        
        Args:
            prompt: The user's prompt
            stream: Whether to use streaming response
        """
        try:
            if stream:
                await self._handle_prompt_stream(prompt)
            else:
                await self._handle_prompt_nonstream(prompt)
        except Exception as e:
            print_error(f"Failed to process prompt: {e}")
    
    async def _handle_prompt_nonstream(self, prompt: str) -> None:
        """Handle non-streaming prompt response"""
        try:
            response = await self.session.send_prompt(prompt)
            print(response)
            print_response_footer()
        except Exception as e:
            print_error(str(e))
    
    async def _handle_prompt_stream(self, prompt: str) -> None:
        """Handle streaming prompt response with rich formatting"""
        in_tool_phase = False
        
        try:
            async for event in self.session.send_prompt_stream(prompt):
                if event.type == EventType.TOOL_PHASE_START:
                    in_tool_phase = True
                    console.print()
                    console.print(
                        Panel(
                            "🔧 [bold yellow]Tool Calls[/bold yellow]",
                            border_style="yellow",
                            padding=(0, 1)
                        )
                    )
                
                elif event.type == EventType.TOOL_CALL:
                    console.print(f"  [bold yellow]→[/bold yellow] [cyan]{event.content}[/cyan]")
                
                elif event.type == EventType.TOOL_RESULT:
                    lines = event.content.strip().split('\n')
                    if len(lines) == 1 and len(event.content) < 80:
                        console.print(f"  [bold blue]←[/bold blue] [dim]{event.content}[/dim]")
                    else:
                        console.print(f"  [bold blue]←[/bold blue] [dim]{lines[0]}[/dim]")
                        for line in lines[1:]:
                            console.print(f"      {line}")
                
                elif event.type == EventType.TOOL_PHASE_END:
                    in_tool_phase = False
                    console.print()
                    console.print(
                        Panel(
                            "📝 [bold cyan]Response[/bold cyan]",
                            border_style="cyan",
                            padding=(0, 1)
                        )
                    )
                
                elif event.type == EventType.CHUNK:
                    print(event.content, end="", flush=True)
                
                elif event.type == EventType.COMPLETE:
                    # Message history is updated, ready for next prompt
                    print()  # Final newline
                
                elif event.type == EventType.ERROR:
                    print_error(f"Agent error: {event.content}")
            
            print_response_footer()
        
        except Exception as e:
            print_error(str(e))
    
    async def handle_allow_command(self, dir_path: str) -> None:
        """Handle /allow command"""
        try:
            result = await self.session.add_allowed_dir(dir_path)
            if result.get("status") == "ok":
                print_success(f"Added allowed directory: {result.get('path')}")
            else:
                print_error(result.get("message", "Unknown error"))
        except Exception as e:
            print_error(f"Failed to add allowed directory: {str(e)}")
    
    async def handle_server_command(self, subcommand: Optional[str]) -> None:
        """Handle /server commands"""
        if subcommand is None:
            print_info("Usage: /server [start|stop|restart|status]")
            return

        subcommand = subcommand.lower()
        
        if subcommand == "start":
            print_info("Starting agent server...")
            if self.session.start_server():
                await asyncio.sleep(1)
                print_success("Agent server started")
            else:
                print_error("Failed to start agent server")
        
        elif subcommand == "stop":
            print_info("Stopping agent server...")
            if self.session.stop_server():
                print_success("Agent server stopped")
            else:
                print_error("Failed to stop agent server")
        
        elif subcommand == "restart":
            print_info("Restarting agent server...")
            if self.session.restart_server():
                await asyncio.sleep(1)
                try:
                    await self.session.sync_allowed_dirs()
                except Exception:
                    pass  # Best effort
                print_success("Agent server restarted")
            else:
                print_error("Failed to restart agent server")
        
        elif subcommand == "status":
            if self.session.is_server_running():
                pid = self.session.get_server_pid()
                print_success(f"Agent server is running (PID: {pid})")
            else:
                print_error("Agent server is not running")
        
        else:
            print_error(f"Unknown server command: {subcommand}")
            print_info("Usage: /server [start|stop|restart|status]")
    
    async def handle_command(self, prompt: str) -> int:
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
                await self.handle_allow_command(parts[1])
            else:
                print_error("Usage: /allow <directory_path>")
        
        elif command == "clear":
            self.session.clear_history()
            print_success("Message history cleared")
        
        elif command == "server":
            await self.handle_server_command(parts[1] if len(parts) > 1 else None)
        
        elif command == "help":
            print_help()
        
        else:
            print_error(f"Unknown command: /{command}")
        
        return 0
    
    async def run_interactive(self) -> None:
        """Run the main interactive loop"""
        print_welcome()
        console.print()
        
        if not await self.initialize():
            return
        
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
                    if await self.handle_command(prompt) == 1:
                        break
                    continue
                
                # Run agent and display response
                await self.handle_prompt(prompt, stream=True)
        
        except KeyboardInterrupt:
            console.print()
            print_info("Exiting...")
            return
        
        finally:
            self.session.stop_server()
            console.print()

