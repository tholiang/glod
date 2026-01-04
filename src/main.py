"""
GLOD - AI Code Editor

Entrypoint for the GLOD CLI application.
Can run either standard CLI or fullscreen TUI based on --tui flag.
"""
import asyncio
import sys
from pathlib import Path
from cli import CLI
from tui_editor import GlodTUIEditor


def main():
    """Main entrypoint for the GLOD CLI/TUI"""
    # Check if --tui flag is provided
    use_tui = "--tui" in sys.argv
    
    try:
        if use_tui:
            # Run fullscreen TUI
            editor = GlodTUIEditor(project_root=Path.cwd())
            asyncio.run(editor.run())
        else:
            # Run standard CLI
            cli = CLI()
            asyncio.run(cli.run_interactive())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

