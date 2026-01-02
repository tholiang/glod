"""
GLOD Client Library - Core client logic and formatting utilities

Provides:
- Rich formatting utilities for CLI output
- Client initialization and session management
- Command handling and interactive loop
- Agent communication orchestration
"""
import os
import asyncio
from pathlib import Path
from typing import Optional, Callable

from client_agent import AgentClient
from rich.panel import Panel
from server_manager import ServerManager

from util import print_error, print_help, print_info, print_response_footer, print_response_header, print_success, print_welcome, get_console

console = get_console()

# Client Session Management
class ClientSession:
    """Manages a client session with the agent"""
    
    def __init__(self, project_root: Path | None = None):
        """
        Initialize a client session.
        
        Args:
            project_root: Root directory for the project (defaults to current working directory)
        """
        if project_root is None:
            project_root = Path(os.getcwd())
        
        self.project_root = project_root
        self.agent_client: Optional[AgentClient] = None
        self.server_manager = ServerManager(project_root=project_root)
        self.allowed_dirs: list[str] = []
    
    async def initialize(self) -> bool:
        """
        Initialize the session and ensure server is running.
        
        Returns:
            True if initialization successful, False otherwise
        """
        # Initialize client
        self.agent_client = AgentClient()
        self.allowed_dirs = [os.getcwd()]
        
        # Check and start server if needed
        if not await self.agent_client.health_check():
            print_error("Agent server is not running")
            print_info("Starting agent server automatically...\n")
            
            if not self.server_manager.start():
                print_error("Failed to start agent server. Exiting.")
                return False
            
            await asyncio.sleep(1)
            
            if not await self.agent_client.health_check():
                print_error("Agent server failed to respond after starting")
                return False
        
        print_success("Agent server is running")
        print_success("Connected to agent server!")
        await self._sync_allowed_dirs()
        print_info("Type [yellow]/help[/yellow] for commands\n")
        
        return True
    
    async def send_prompt(self, prompt: str, stream: bool = True) -> None:
        """
        Send a prompt to the agent and display the response.
        
        Args:
            prompt: The user's prompt
            stream: Whether to use streaming response
        """
        if not self.agent_client:
            print_error("Agent client not initialized")
            return
        
        # Set up event handlers for better formatting
        def on_tool_phase_start():
            """Called when entering tool call/result phase"""
            console.print()
            console.print(Panel("🔧 [bold yellow]Tool Calls[/bold yellow]", border_style="yellow", padding=(0, 1)))
        
        def on_tool_call(content: str):
            """Handle tool call event"""
            console.print(f"  [bold yellow]→[/bold yellow] [cyan]{content}[/cyan]")
        
        def on_tool_result(content: str):
            """Handle tool result event"""
            lines = content.strip().split('\n')
            if len(lines) == 1 and len(content) < 80:
                console.print(f"  [bold blue]←[/bold blue] [dim]{content}[/dim]")
            else:
                console.print(f"  [bold blue]←[/bold blue] [dim]{lines[0]}[/dim]")
                for line in lines[1:]:
                    console.print(f"      {line}")
        
        def on_tool_phase_end():
            """Called when exiting tool call/result phase"""
            console.print()
            console.print(Panel("📝 [bold cyan]Response[/bold cyan]", border_style="cyan", padding=(0, 1)))
        
        def on_chunk(content: str):
            """Handle response chunk"""
            print(content, end="", flush=True)
        
        # Register handlers
        self.agent_client.on_tool_phase_start = on_tool_phase_start
        self.agent_client.on_tool_call = on_tool_call
        self.agent_client.on_tool_result = on_tool_result
        self.agent_client.on_tool_phase_end = on_tool_phase_end
        self.agent_client.on_chunk = on_chunk
        
        if stream:
            await self.agent_client.run_stream(prompt)
        else:
            await self.agent_client.run(prompt)
        
        print_response_footer()
    
    async def _handle_allow_dir_command(self, dir_path: str) -> None:
        """Handle /allow commands to add allowed directories"""
        if not self.agent_client:
            print_error("Agent client not initialized")
            return
        
        abs_path = os.path.abspath(dir_path)
        
        if not os.path.isdir(abs_path):
            print_error(f"Directory does not exist: {abs_path}")
            return
        
        if abs_path not in self.allowed_dirs:
            self.allowed_dirs.append(abs_path)
        
        try:
            await self.agent_client.add_allowed_dir(abs_path)
            print_success(f"Added allowed directory: {abs_path}")
        except Exception as e:
            print_error(f"Failed to add allowed directory: {str(e)}")
    
    async def _sync_allowed_dirs(self) -> None:
        """Sync allowed directories with server"""
        for dir_path in self.allowed_dirs:
            await self._handle_allow_dir_command(dir_path)
    
    async def _handle_server_command(self, subcommand: Optional[str]) -> None:
        """Handle /server commands"""
        if subcommand is None:
            print_info("Usage: /server [start|stop|restart|status]")
            return

        subcommand = subcommand.lower()
        
        if subcommand == "start":
            print_info("Starting agent server...")
            self.server_manager.start()
            await asyncio.sleep(1)
            print_success("Agent server started")
        
        elif subcommand == "stop":
            print_info("Stopping agent server...")
            self.server_manager.stop()
            print_success("Agent server stopped")
        
        elif subcommand == "restart":
            print_info("Restarting agent server...")
            self.server_manager.restart()
            await asyncio.sleep(1)
            await self._sync_allowed_dirs()
            print_success("Agent server restarted")
        
        elif subcommand == "status":
            if self.server_manager.is_running():
                pid = self.server_manager.get_pid()
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
                await self._handle_allow_dir_command(parts[1])
            else:
                print_error("Usage: /allow <directory_path>")
        
        elif command == "clear":
            if self.agent_client:
                self.agent_client.clear_history()
                print_success("Message history cleared")
        
        elif command == "server":
            await self._handle_server_command(parts[1] if len(parts) > 1 else None)
        
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
                await self.send_prompt(prompt, stream=True)
        
        except KeyboardInterrupt:
            console.print()
            print_info("Exiting...")
            return
        
        finally:
            self.server_manager.stop()
            console.print()

