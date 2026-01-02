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

Responsive two-column layout that adapts to terminal size:
- **Header** - Title and processing status indicator (fixed 3 lines)
- **Messages** - Last 20 messages with user/agent distinction (60% width, flexible height)
- **Input Section** (40% width, flexible):
  - **Status** - Server health, message/directory count (fixed 2 lines)
  - **Input** - Multi-line input area (flexible)
- **Footer** - Quick command reference (fixed 3 lines)

## Usage

```bash
python src/main.py          # Run fullscreen TUI editor
```

## Implementation

`GlodTUIEditor` class wraps `AgentClient` and `ServerManager`:
- Manages message history locally
- Routes commands through `_handle_command()`
- Streams agent responses directly into history
- Non-blocking input via async executor

Layout uses ratio-based sizing:
- Fixed-size panels (header, footer, status) don't scale
- Flexible panels (messages, input) use ratios (3:1) to maintain proportions
- Panel expansion enabled for better space utilization

## Architecture Notes

- **Rich Live + Layout** - `Live` renders fullscreen with 4 FPS refresh, `Layout` manages split panels with ratios
- **Responsive Design** - Ratios and `expand=True` ensure layouts scale with terminal
- **Event Handlers** - Agent responses streamed via `on_chunk` callback
- **Message History** - Stored as list of tuples, last 20 shown (scrolls automatically)
- **Input Buffering** - Character-by-character input accumulation for real-time feedback
- **Async Input** - Uses `loop.run_in_executor()` to prevent blocking the Live display


