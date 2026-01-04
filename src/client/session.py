"""
Client session management - Pure business logic, no output handling.

Manages:
- Client-server communication
- Message history
- Allowed directories
- Server lifecycle (via ServerManager)
"""
import os
import asyncio
from pathlib import Path
from typing import Optional

from .agent_client import AgentClient, StreamEvent, EventType
from ..server_manager import ServerManager


class ClientSession:
    """
    Manages a client session with the agent.
    
    This class handles:
    - Server initialization and health checks
    - Sending prompts and streaming responses
    - Managing allowed directories
    - Server lifecycle management
    
    Does not handle user input or output presentation.
    All responses are returned to the caller.
    """
    
    def __init__(self, project_root: Optional[Path] = None):
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
            if not self.server_manager.start():
                return False
            
            await asyncio.sleep(1)
            
            if not await self.agent_client.health_check():
                return False
        
        await self._sync_allowed_dirs()
        return True
    
    async def send_prompt(self, prompt: str) -> str:
        """
        Send a prompt to the agent and return the complete response.
        
        Args:
            prompt: The user's prompt
        
        Returns:
            The complete response text from the agent
        
        Raises:
            RuntimeError: If agent client not initialized
            Exception: If agent communication fails
        """
        if not self.agent_client:
            raise RuntimeError("Agent client not initialized")
        
        return await self.agent_client.run(prompt)
    
    async def send_prompt_stream(self, prompt: str):
        """
        Send a prompt to the agent and stream the response.
        
        Args:
            prompt: The user's prompt
        
        Yields:
            StreamEvent objects representing the response stream
        
        Raises:
            RuntimeError: If agent client not initialized
        """
        if not self.agent_client:
            raise RuntimeError("Agent client not initialized")
        
        async for event in self.agent_client.run_stream(prompt):
            yield event
    
    async def add_allowed_dir(self, dir_path: str) -> dict:
        """
        Add a directory to the allowed paths.
        
        Args:
            dir_path: The directory path to allow
        
        Returns:
            Status dict with keys:
            - "status": "ok" or "error"
            - "message": Status message
            - "path": The absolute path (if successful)
        """
        if not self.agent_client:
            return {
                "status": "error",
                "message": "Agent client not initialized"
            }
        
        abs_path = os.path.abspath(dir_path)
        
        if not os.path.isdir(abs_path):
            return {
                "status": "error",
                "message": f"Directory does not exist: {abs_path}"
            }
        
        if abs_path not in self.allowed_dirs:
            self.allowed_dirs.append(abs_path)
        
        result = await self.agent_client.add_allowed_dir(abs_path)
        if result.get("status") == "ok":
            result["path"] = abs_path
        return result
    
    async def sync_allowed_dirs(self) -> None:
        """Sync allowed directories with server"""
        await self._sync_allowed_dirs()
    
    async def _sync_allowed_dirs(self) -> None:
        """Internal method to sync allowed directories"""
        for dir_path in self.allowed_dirs:
            if self.agent_client:
                await self.agent_client.add_allowed_dir(dir_path)
    
    def clear_history(self) -> None:
        """Clear the message history"""
        if self.agent_client:
            self.agent_client.clear_history()
    
    def start_server(self) -> bool:
        """Start the agent server"""
        return self.server_manager.start()
    
    def stop_server(self) -> bool:
        """Stop the agent server"""
        return self.server_manager.stop()
    
    def restart_server(self) -> bool:
        """Restart the agent server"""
        return self.server_manager.restart()
    
    def is_server_running(self) -> bool:
        """Check if the agent server is running"""
        return self.server_manager.is_running()
    
    def get_server_pid(self) -> Optional[int]:
        """Get the agent server process ID if running"""
        return self.server_manager.get_pid()

