# CLI Interface

Uses Typer + Rich for beautiful, modern terminal UI.

## Features

- **Rich formatted output**: Colors, panels, tables for visual hierarchy
- **Typer commands**: Structured command handling with validation
- **Styled prompts**: Cyan colored `>` prompt with clear visual feedback
- **Status messages**: Green checkmarks for success, red X for errors, blue info icons
- **Distinct tool display**: Tool calls and results visually separated from agent response
- **Tool phase tracking**: Yellow "Tool Calls" panel header, Cyan "Response" panel header
- **Help tables**: Commands displayed in formatted tables

## Display Components

### Status Functions
- `print_success()` - Green checkmark + message
- `print_error()` - Red X + message
- `print_info()` - Blue info icon + message
- `print_welcome()` - Cyan title panel on startup
- `print_help()` - Formatted command table

### Tool Call Rendering
Tool calls and results flow through event handlers in `_entry()`:

- `on_tool_phase_start()` - Yellow panel: "🔧 Tool Calls"
- `on_tool_call(content)` - Yellow arrow `→` with cyan tool name and args
## Command Handling

Commands prefixed with `/` are handled via `_command()`. Returns 0 to continue, 1 to exit.

Server control uses `_handle_server_command()` for start/stop/restart/status.

Directory allowlist managed client-side via `/allow <dir>` command:
- Validates directory exists before adding
- Maintains local list of allowed directories
- Syncs with agent on each request

History and directories synced with `_sync_allowed_dirs()`.

