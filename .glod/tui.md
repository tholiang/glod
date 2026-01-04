# Fullscreen TUI Editor

`src/tui_editor.py` implements a fullscreen terminal UI using Rich layouts and message streaming. The TUI is an alternative interface to the standard CLI.

## Class: GlodTUIEditor

### Initialization
- `__init__(project_root)` - Creates ClientSession for business logic, initializes message history, scroll offset tracking

### Main Loop
- `run()` - Async main loop:
  1. Calls `session.initialize()` to start server
  2. Displays welcome message
  3. Prompts for user input
  4. Routes to `_send_message()` or `_handle_command()`
  5. After agent response, calls `_prompt_for_scrolling()` to allow browsing
  6. Exits on `/exit` command

### Message Scrolling
- `_prompt_for_scrolling()` - Interactive scroll mode after responses:
  - Only activates if message history exceeds display height
  - Displays paginated view of all messages
  - Supports: `u`/`up` (scroll up 3 lines), `d`/`down` (scroll down 3 lines), `t`/`top` (jump to top), `b`/`bottom` (jump to bottom), `q`/`quit`/`enter` (exit scroll mode)
  - Shows scroll position as percentage and line numbers

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
  - Messages: Message history with scrolling offset, showing position indicator
  - Footer: Command help
  - Properly handles line wrapping and scroll bounds

## Event Flow

```
User input → _handle_command() or _send_message()
  → session methods / StreamEvent objects
  → _render_screen() updates display
  → Message added to history
  → _prompt_for_scrolling() offers interactive browsing
  → Ready for next input
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

- `clear_history()` - Sync agent history
- `start_server()`, `stop_server()`, `restart_server()` - Server lifecycle
- `is_server_running()`, `get_server_pid()` - Server status
- `sync_allowed_dirs()` - Re-sync after restart
- `allowed_dirs` - List of allowed directories (read-only)

The TUI never imports AgentClient directly; all communication is through ClientSession.

