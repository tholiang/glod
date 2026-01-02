# Client Library - Rich Formatting Utilities

`src/client_lib.py` provides console output functions with Rich formatting for the CLI.

## Functions

- `print_welcome()` - Cyan/yellow GLOD header panel
- `print_success(msg)` - Green ✓ prefix
- `print_error(msg)` - Red ✗ prefix
- `print_info(msg)` - Blue ℹ prefix
- `print_response_header(title)` - Cyan panel header for agent responses
- `print_response_footer()` - Footer spacing after responses
- `get_console()` - Returns Rich Console instance for direct access

## Design

Exported as module-level functions that share a single `Console` instance. Used by `main.py` for all formatted output.

