# Fullscreen TUI Editor

`src/tui_editor.py` implements a fullscreen terminal UI for GLOD using Rich's Live display with message streaming.

## Architecture

`GlodTUIEditor` wraps a `ClientSession` (from `client_lib.py`):
- Session manages server startup, initialization, agent connection, allowed dirs
- TUI provides fullscreen display and message-based UI
- Command handlers use session's state/manager objects directly

## Features

- **Interactive message interface** - User/agent message history in scrollable panel
- **Real-time streaming** - Agent responses display live as they stream
- **Status bar** - Live server status, dir count, message count
- **Command palette** - `/help`, `/clear`, `/allow`, `/server`, `/exit`
- **Layout-based UI** - Rich Layout with header, status, messages, footer panels

## Implementation

`GlodTUIEditor.__init__(session: ClientSession)` takes a pre-initialized session:
- `_send_message()` - Streams agent response into message history with Live display updates
- `_handle_command()` - Routes `/commands` to specific handlers
- `_handle_allow_dir()` / `_handle_server_command()` - Delegate to session's state/managers, display results in TUI
- `_show_help()` - Display help as agent message

TUI commands do NOT call session.handle_*() methods (which print to console). Instead, they:
1. Call session state methods directly (ServerManager, AgentClient)
2. Append results to message history for display

## Design Notes

- **Thin display layer** - TUI is UI-only, relies on ClientSession for core logic
- **Message-based feedback** - Commands display feedback in message history, not console
- **Streaming via stream_run()** - Uses AgentClient.stream_run() generator, not stream_run_print()
- **State sharing** - TUI directly accesses session.allowed_dirs, session.server_manager

