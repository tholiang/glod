# Fullscreen TUI Editor

`src/tui_editor.py` implements a fullscreen terminal UI for GLOD using Rich's `Live` and `Layout`.

## Features

- **Fullscreen interface** - Runs as standalone editor, not in bash
- **Message history** - Scrollable display of conversation with agent
- **Multi-line input** - Input area that supports multiple lines
- **Status bar** - Real-time server status, message count, allowed dirs
- **Command palette** - `/help`, `/clear`, `/allow`, `/server`, `/exit`
- **Streaming responses** - Real-time agent response display

## Layout

Four-panel layout:
- **Header** - Title and processing status indicator
- **Messages** - Last 20 messages with user/agent distinction
- **Status** - Server health, message count, directory count
- **Input** - Multi-line input area (up to 5 lines visible)
- **Footer** - Quick command reference

## Usage

```bash
python src/main.py          # Default: fullscreen TUI mode
python src/main.py --cli    # Legacy CLI mode
```

## Implementation

`GlodTUIEditor` class wraps `AgentClient` and `ServerManager`:
- Manages message history locally
- Routes commands through `_handle_command()`
- Streams agent responses directly into history
- Non-blocking input via async executor

## Multi-Line Input

Input is line-buffered. Type normally and press Enter to accumulate lines, then use command to submit (e.g., `/exit` to quit, or send message after input is ready).



## Architecture Notes

- **Rich Live + Layout** - `Live` renders fullscreen with 2 FPS refresh, `Layout` manages split panels
- **Event Handlers** - Agent responses streamed via `on_chunk` callback
- **Message History** - Stored as list of tuples, last 20 shown (scrolls automatically)
- **Input Buffering** - Each typed line accumulates in `input_lines[]` for multi-line support
- **Async Input** - Uses `loop.run_in_executor()` to prevent blocking the Live display

