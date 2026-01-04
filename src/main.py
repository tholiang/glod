"""
GLOD - AI Code Editor

Entrypoint for the GLOD CLI application.
"""
import asyncio
from cli import CLI


def main():
    """Main entrypoint for the GLOD CLI"""
    try:
        cli = CLI()
        asyncio.run(cli.run_interactive())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

    main()

