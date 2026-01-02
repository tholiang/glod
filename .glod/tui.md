# Fullscreen TUI Editor

`src/tui_editor.py` implements a fullscreen terminal UI using Rich layouts and message streaming.

## Architecture

Pure consumption of AsyncGenerators from `ClientSession`:
- `ClientSession` returns `AsyncGenerator[str, None]` for all operations
- `GlodTUIEditor` consumes generators and formats output for display
- No business logic in TUI - it's purely a display layer
- No console side effects in core logic

## Features

- **Message interface** - Scrollable user/agent message history
- **Real-time streaming** - Agent responses display live as chunks arrive
- **Status bar** - Server status, directory count, message count
- **Commands** - `/help`, `/clear`, `/allow`, `/server`, `/exit`
- **Status formatting** - Color-coded Rich markup for status messages

## Implementation

Key methods:

- `_send_message(msg)` - Stream agent response to message history
- `_handle_command(cmd)` - Route `/commands` to session generators
- `_format_status_message(msg)` - Apply Rich markup (✓→green, ℹ→blue, Error:→red)
- `_show_help()` - Display help text in message history

Command flow:
```
User input → _handle_command()
  → session.handle_allow_dir_command() / handle_server_command()
  → Consume AsyncGenerator[str, None]
  → _format_status_message() adds Rich markup
  → Append to message history
```

## Design

- **Thin display layer** - All logic delegated to ClientSession
- **Pure generators** - No print/console calls in core code
- **Rich formatting** - Status messages colored based on type
- **Streaming UI** - Live display updates during agent response streaming

