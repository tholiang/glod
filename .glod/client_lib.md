# Client Library

`src/client_lib.py` provides the core client logic for the GLOD CLI.

## Formatting Utilities

- `print_welcome()` - Cyan/yellow GLOD header panel
- `print_success(msg)` - Green ✓ prefix
- `print_error(msg)` - Red ✗ prefix
- `print_info(msg)` - Blue ℹ prefix
- `print_response_header(title)` - Cyan panel header for agent responses
- `print_response_footer()` - Footer spacing after responses
- `print_help()` - Table of available commands
- `get_console()` - Returns Rich Console instance

## ClientSession

Manages a client session with the agent. Encapsulates:
- Agent client and server manager initialization
- Prompt sending with streaming and event handlers
- Command processing (/allow, /server, /clear, /help, /exit)
- Interactive REPL loop

**Key Methods:**
- `initialize()` - Ensure server is running and connected
- `send_prompt(prompt, stream)` - Send prompt and display response with event handlers
- `handle_command(prompt)` - Process /commands
## Architecture

- **Formatting** functions share a single Console instance
- **ClientSession** coordinates agent client, server manager, and state
- **Event handlers** registered with agent client for tool call/result display
