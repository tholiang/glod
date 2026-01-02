"""
GLOD CLI - Beautiful AI Code Editor Interface

Entrypoint for the CLI application. Delegates to client_lib for core logic.
"""
import os
import asyncio
from pathlib import Path

from client_lib import ClientSession, get_console


console = get_console()


def main():
    """Main entrypoint for the GLOD CLI"""
    try:
        asyncio.run(_run_interactive())
    except KeyboardInterrupt:
        pass


async def _run_interactive():
    """Initialize session and run interactive loop"""
    session = ClientSession(project_root=Path(os.getcwd()))
    await session.run_interactive()


if __name__ == "__main__":
    main()

