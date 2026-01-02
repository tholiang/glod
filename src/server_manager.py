"""
Server manager for starting/stopping the agent server as a subprocess.

Handles:
- Starting the agent server in a subprocess
- Stopping/killing the agent server
- Restarting the agent server
- Health checks
- Finding existing processes by port
"""
import subprocess
import sys
import time
import asyncio
import socket
from pathlib import Path
from util import print_success, print_error, print_info


class ServerManager:
    """Manages the agent server subprocess"""
    
    def __init__(self, project_root: Path | None = None):
        self.process = None
        # project_root defaults to the directory from which the CLI was invoked
        self.project_root = project_root or Path.cwd()


    def _is_port_in_use(self, port: int = 8000) -> bool:
        """Check if the server port is already in use (indicates server is running)"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                result = sock.connect_ex(('127.0.0.1', port))
                return result == 0
        except Exception:
            return False
    
    def start(self) -> bool:
        """
        Start the agent server as a subprocess.
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.process is not None and self.process.poll() is None:
            print_info(f"Agent server is already running (PID: {self.process.pid})")
            return True
        
        try:
            # Start the server using python -m
            self.process = subprocess.Popen(
                [sys.executable, "-m", "server.agent_server"],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Give the server a moment to start
            time.sleep(1)
            
            # Check if process is still running
            if self.process.poll() is None:
                print_success(f"Agent server started (PID: {self.process.pid})")
                return True
            else:
                # Process died immediately
                _, stderr = self.process.communicate()
                print_error(f"Failed to start agent server:\n{stderr}")
                self.process = None
                return False
                
        except Exception as e:
            print_error(f"Error starting agent server: {e}")
            self.process = None
            return False
            
    def stop(self) -> bool:
        """
        Stop the agent server gracefully.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        stopped = False
        
        # Check if we have a process reference
        if self.process is not None and self.process.poll() is None:
            try:
                self.process.terminate()
                # Wait up to 5 seconds for graceful shutdown
                try:
                    self.process.wait(timeout=5)
                    print_success("Agent server stopped")
                    self.process = None
                    stopped = True
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown times out
                    if self.process is not None:
                        self.process.kill()
                        self.process.wait()
                        print_success("Agent server killed")
                    self.process = None
                    stopped = True
                    
            except Exception as e:
                print_error(f"Error stopping agent server: {e}")
                self.process = None
                return False
        
        # If no process reference but port is in use, kill the process on that port
        if not stopped and self._is_port_in_use(8000):
            print_info("No local process reference, but server is running on port 8000. Attempting to kill...")
            try:
                # Use lsof to find and kill the process on port 8000
                result = subprocess.run(
                    ["lsof", "-ti:8000"],
                    capture_output=True,
                    text=True
                )
                if result.stdout.strip():
                    pid = result.stdout.splitlines()[0].strip()
                    subprocess.run(["kill", pid])
                    time.sleep(1)
                    print_success(f"Agent server killed (PID: {pid})")
                    stopped = True
            except Exception as e:
                print_error(f"Error killing process on port 8000: {e}")
                return False
        
        # If nothing was stopped, log it only if port is truly not in use
        if not stopped and not self._is_port_in_use(8000):
            print_info("Agent server is not running")
        
        return True
    
    def restart(self) -> bool:
        """
        Restart the agent server.
        
        Returns:
            True if restarted successfully, False otherwise
        """
        print_info("Restarting agent server...")
        self.stop()
        time.sleep(2)  # Give server more time to fully initialize after restart
        return self.start()
    
    def is_running(self) -> bool:
        """Check if the agent server process is running"""
        if self.process is None:
            return False
        return self.process.poll() is None
    
    def get_pid(self) -> int | None:
        """Get the process ID if running, None otherwise"""
        if self.is_running() and self.process is not None:
            return self.process.pid
        return None
