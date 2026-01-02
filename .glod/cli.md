# CLI Interface

Uses Typer + Rich for beautiful, modern terminal UI.

## Features

- **Rich formatted output**: Colors, panels, tables for visual hierarchy
- **Typer commands**: Structured command handling with validation
- **Styled prompts**: Cyan colored `>` prompt with clear visual feedback
- **Status messages**: Green checkmarks for success, red X for errors, blue info icons
- **Response separation**: Tool calls/results visually separated from final agent response
- **Tool phase tracking**: Clear panel headers when agent executes tools
- **Help tables**: Commands displayed in formatted tables

## Display Components

### Status Functions
- `print_success()` - Green checkmark + message
- `print_error()` - Red X + message
- `print_info()` - Blue info icon + message
- `print_welcome()` - Cyan title panel on startup
- `print_help()` - Formatted command table

### Response Handling
- `print_response_footer()` - Space after agent output
- Event handlers in `_entry()` for real-time formatting:
  - `on_tool_phase_start()` - "🔧 Tool Calls" panel
  - `on_tool_call(content)` - Format tool invocation with arrows
  - `on_tool_result(content)` - Format result with response arrow
  - `on_tool_phase_end()` - "📝 Response" panel header
  - `on_chunk(content)` - Direct output of final response text

## Command Handling

Commands prefixed with `/` are handled via `_command()`. Returns 0 to continue, 1 to exit.

Server control uses `_handle_server_command()` for start/stop/restart/status.

History and directories synced with `_sync_allowed_dirs()`.

