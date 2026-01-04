# Fullscreen TUI Editor

`src/tui_editor.py` implements a fullscreen terminal UI using Rich layouts and message streaming. The TUI is an alternative interface to the standard CLI.

## Mouse & Keyboard Support

The TUI supports both mouse and keyboard input for scrolling:
- **Mouse scrolling**: Use trackpad/mouse wheel to scroll through message history (uses ANSI mouse reporting)
- **Keyboard**: Arrow keys (↑/↓), u/d (up/down 3 lines), t/b (top/bottom), q/enter (quit scroll mode)
- Terminal mouse support is enabled/disabled via ANSI escape codes

### Mouse Support Implementation

- `_enable_mouse_support()` - Enables mouse tracking on Unix-like systems using ANSI codes (1000, 1015)
- `_disable_mouse_support()` - Disables mouse tracking on exit
- `_parse_mouse_input(input_str)` - Parses mouse wheel events from terminal input:
  - Detects mouse wheel up/down sequences
  - Returns 'up' or 'down' direction, or None if not a mouse event

### Message Scrolling with Mouse/Keyboard

- `_prompt_for_scrolling()` - Interactive scroll mode after responses:
  - Only activates if message history exceeds display height
  - Enables mouse support and captures keyboard/mouse input
  - Mouse wheel events parsed via `_parse_mouse_input()`
  - Supports: arrow keys (↑/↓), u/d (3 lines), t/b (top/bottom), q/enter (exit)
  - Shows scroll position as percentage and line numbers
  - Disables mouse support on exit or interrupt

```


## Main Architecture

### Initialization and Startup

- `__init__(project_root)` - Creates ClientSession, initializes message history, scroll state

### Main Loop

- `run()` - Async main loop:
  1. Initializes ClientSession (starts server)
  2. Displays welcome message
  3. Prompts for user input via `console.input()`
  4. Routes to `_send_message()` or `_handle_command()`
  5. After agent response, calls `_prompt_for_scrolling()` for interactive browsing
  6. Exits on `/exit` command or interrupt

### Message Rendering

- `_render_screen()` - Renders complete screen layout with:
  - Header with processing status
  - Server status and allowed directories count
  - Messages panel with scrolling indicator
  - Footer with available commands

### Commands

- `_handle_command()` - Routes commands (/help, /clear, /allow, /server, /exit)
- `_handle_server_command()` - Manages server lifecycle (start, stop, restart, status)
- `_show_help()` - Displays help in message history

### Message Sending & Streaming

- `_send_message()` - Sends prompt to agent with streaming display:
  - Creates Live display for real-time updates
  - Streams response events and tool calls
  - Updates display for each event type
  - Adds final response to message history

