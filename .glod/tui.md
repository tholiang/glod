# Fullscreen TUI Editor

`src/tui_editor.py` implements a fullscreen terminal UI using Rich layouts and message streaming. The TUI is an alternative interface to the standard CLI.

## Class: GlodTUIEditor

### Initialization
- `__init__(project_root)` - Creates ClientSession for business logic, initializes message history

### Main Loop
- `run()` - Async main loop:
  1. Calls `session.initialize()` to start server
  2. Displays welcome message
  3. Prompts for user input
  4. Routes to `_send_message()` or `_handle_command()`
  5. Exits on `/exit` command

### Message Streaming
- `_send_message(msg)` - Sends prompt via `session.send_prompt_stream()`:
  - Adds user message to history
  - Uses Live display for real-time streaming
  - Consumes StreamEvent objects from async generator
  - Handles CHUNK events to build response
  - Adds final response to message history

### Command Handling
- `_handle_command(cmd)` - Routes `/` commands:
  - `/exit` - Set exit flag
  - `/help` - Display help text in messages
  - `/clear` - Clear history via `session.clear_history()`
  - `/allow <path>` - Call `session.add_allowed_dir()`
  - `/server [start|stop|restart|status]` - Delegate to `_handle_server_command()`

- `_handle_server_command(subcmd)` - Server lifecycle:
  - `start` - Call `session.start_server()`
  - `stop` - Call `session.stop_server()`
  - `restart` - Call `session.restart_server()`, sync dirs
  - `status` - Call `session.is_server_running()`, `get_server_pid()`

### Display Rendering
- `_render_screen()` - Returns Layout with:
  - Header: Editor title with processing indicator
  - Status: Server status and allowed directory count
  - Messages: Message history with streaming response
  - Footer: Command help

- `_format_status_message(msg)` - Applies Rich markup based on message prefix (unused, kept for compatibility)

- `_show_help()` - Displays command list in message history

## Event Flow

```
User input → _handle_command()
  → session.add_allowed_dir() / send_prompt_stream() / server methods
  → Consume return values and StreamEvent objects
  → Format and append to message history
  → Display via _render_screen() and Rich Live
```

## Integration with ClientSession

The TUI uses these ClientSession methods:
- `initialize()` - Start server, health check
- `send_prompt_stream()` - Yields StreamEvent objects
- `add_allowed_dir()` - Returns status dict
- `clear_history()` - Sync agent history
- `start_server()`, `stop_server()`, `restart_server()` - Server lifecycle
- `is_server_running()`, `get_server_pid()` - Server status
- `sync_allowed_dirs()` - Re-sync after restart
- `allowed_dirs` - List of allowed directories (read-only)

The TUI never imports AgentClient directly; all communication is through ClientSession.

