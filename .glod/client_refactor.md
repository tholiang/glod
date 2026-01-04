# Client Architecture Refactor

## Overview

Client code is now separated into **business logic** (no output) and **CLI presentation**.

## Structure

```
src/
├── main.py              # Entrypoint, calls CLI
├── cli.py              # CLI handler, output presentation (Rich)
├── server_manager.py   # Server subprocess management
├── client/
│   ├── __init__.py
│   ├── agent_client.py # HTTP client, yields StreamEvent objects
│   └── session.py      # Session management, no output
└── util.py             # Formatting utilities
```

## Key Classes

### AgentClient (`client/agent_client.py`)
- Pure business logic, no I/O or print statements
- Methods:
  - `run(prompt)` → returns response text
  - `run_stream(prompt)` → yields `StreamEvent` objects
  - `add_allowed_dir(dir_path)` → returns status dict
  - `clear_history()` → no return
- **StreamEvent dataclass:**
  - `type: EventType` - TOOL_CALL, TOOL_RESULT, CHUNK, COMPLETE, ERROR, TOOL_PHASE_START, TOOL_PHASE_END
  - `content: str` - event data

### ClientSession (`client/session.py`)
- Manages server lifecycle and session state
- No output handling
- Methods:
  - `initialize()` → bool
  - `send_prompt(prompt)` → str (non-streaming)
  - `send_prompt_stream(prompt)` → AsyncGenerator[StreamEvent]
  - `add_allowed_dir(dir_path)` → dict
  - Server control: `start_server()`, `stop_server()`, `restart_server()`, `is_server_running()`

### CLI (`cli.py`)
- Handles all user interaction and output presentation
- Uses Rich for formatting
- Methods:
  - `handle_prompt(prompt, stream=True)` - dispatches to stream or non-stream handler
  - `_handle_prompt_stream(prompt)` - consumes StreamEvent objects, renders output
  - `handle_*_command()` - command handlers (/allow, /server, /clear, /help, /exit)
  - `run_interactive()` - main event loop

## Event Handling

AgentClient emits StreamEvent objects. CLI interprets them:

```
TOOL_PHASE_START → Display tool panel
TOOL_CALL → Format and display tool call
TOOL_RESULT → Format and display result
TOOL_PHASE_END → Display response panel
CHUNK → Print response text
COMPLETE → Update history
ERROR → Display error
```

## Adding Features

1. **New agent operation:** Add method to `ClientSession`, returns data or yields events
2. **New command:** Add handler to `CLI`, dispatch from `handle_command()`
3. **Custom output:** Consume events in `CLI`, implement presentation logic

