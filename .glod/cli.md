# TUI Interface

Fullscreen terminal UI using Rich's Live layout and Layout components.

## Features

- **Fullscreen editor** - Runs as standalone window, not in bash shell
- **Rich formatted output** - Colors, panels for visual hierarchy
- **Message history** - Scrollable conversation display with agent/user distinction
- **Multi-line input** - Input area supporting multiple lines of text
- **Real-time status** - Server health, message count, allowed directories
- **Status messages** - Green checkmarks for success, red X for errors, blue info icons
- **Streaming responses** - Agent responses appear in real-time

## Layout Panels

- **Header** - App title and processing indicator
- **Messages** - Last 20 messages shown with scrolling
- **Status** - Real-time indicators for server, message count, directories
- **Input** - Multi-line text input (up to 5 lines visible)
- **Footer** - Quick command reference

## Commands

All commands are prefixed with `/`:

- `/help` - Show all available commands
- `/clear` - Clear message history
- `/allow <path>` - Add directory to allowed file access paths
- `/server start|stop|restart|status` - Control agent server
- `/exit` - Exit GLOD

Server control:
- Validates directory existence before adding via `/allow`
- Maintains local list of allowed directories
- Syncs with agent on startup

## Implementation

- Uses `GlodTUIEditor` class from `src/tui_editor.py`
- Async event handlers for streaming responses
- Non-blocking input via executor to prevent display freezing

