# Simple CLI Editor

`src/tui_editor.py` implements a simple sequential CLI interface using Rich. No panels, layouts, or scrolling - just clean input/output flow.

## Main Architecture

### Initialization and Startup

- `__init__(project_root)` - Creates ClientSession, initializes message history

### Main Loop

- `run()` - Async main loop:
  1. Initializes ClientSession (starts server)
  2. Displays welcome message
  3. Prompts for user input via `console.input()`
  4. Routes to `_send_message()` or `_handle_command()`
  5. Exits on `/exit` command or interrupt

### Message Sending & Streaming

- `_send_message()` - Sends prompt to agent with streaming display:
  - Prints blank line before response
  - Streams response chunks directly to console
  - Shows tool calls and results inline
  - Adds final response to message history

### Commands

- `_handle_command()` - Routes commands (/help, /clear, /allow, /server, /status, /exit)
- `_handle_server_command()` - Manages server lifecycle (start, stop, restart, status)
- `_show_help()` - Displays available commands


