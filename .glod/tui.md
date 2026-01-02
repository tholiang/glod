# Fullscreen TUI Editor

`src/tui_editor.py` implements a terminal UI for GLOD using Rich's built-in console input handling.

## Features

- **Interactive interface** - Loop-based display refresh with blocking input
- **Message history** - Display of conversation with agent
- **Status bar** - Real-time server status, message count, allowed dirs
- **Command palette** - `/help`, `/clear`, `/allow`, `/server`, `/exit`
- **Streaming responses** - Real-time agent response display

## Usage

```bash
python src/main.py          # Run interactive TUI editor
```

## Implementation

`GlodTUIEditor` class wraps `AgentClient` and `ServerManager`:
- Manages message history locally
- Uses `Console.input()` for cross-platform input handling (works on macOS)
- Routes commands through `_handle_command()`
- Streams agent responses directly into history
- Blocks on input, updates display after each action

Input flow:
1. Call `_render_display()` to show current state
2. Call `Console.input()` to wait for user input
3. Process input as command or message
4. Repeat

## Design Notes

- **Rich Console.input()** - Cross-platform input handling that works correctly on macOS (replaces manual fcntl/termios)
- **Blocking input** - Simpler than non-blocking with Live refresh, adequate for interactive use
- **Display refresh** - Full screen redraw after each action
- **Message History** - Stored as list of tuples, last 20 shown
- **Error handling** - Graceful handling of EOFError and KeyboardInterrupt

