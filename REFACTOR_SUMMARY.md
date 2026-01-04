# TUI Refactoring Summary

## Overview
Refactored `src/tui_editor.py` in the `fullscreen-tui` branch to correctly use the GLOD client library. The TUI is now a clean presentation layer that properly delegates all business logic to `ClientSession`.

## Key Changes

### 1. Import Fix
**Before:**
```python
from client_lib import ClientSession
```

**After:**
```python
from client import ClientSession, StreamEvent, EventType
```

**Reason:** The `client` module (located in `src/client/`) provides the correct business logic classes. `client_lib` was a misnomer; `util.py` contains the actual formatting utilities.

### 2. StreamEvent Handling
**Before:**
```python
async for chunk in self.session.agent_client.stream_run(
    prompt=message,
    message_history=history_text
):
    self.streaming_response += chunk
```

**After:**
```python
async for event in self.session.send_prompt_stream(message):
    if event.type == EventType.CHUNK:
        self.streaming_response += event.content
    elif event.type == EventType.COMPLETE:
        pass  # Message history updated in client
    elif event.type == EventType.ERROR:
        self.streaming_response += f"[red]Error: {event.content}[/red]"
```

**Reason:** 
- The correct method is `ClientSession.send_prompt_stream()` (not `agent_client.stream_run()`)
- Yields `StreamEvent` objects with type and content fields
- Caller must check event type to handle appropriately
- ClientSession handles history management internally

### 3. Command Handler Refactoring

#### `/allow` Command
**Before:**
```python
async for message in self.session.handle_allow_dir_command(parts[1]):
    self.messages.append(("agent", self._format_status_message(message)))
```

**After:**
```python
result = await self.session.add_allowed_dir(parts[1])
if result.get("status") == "ok":
    self.messages.append(("agent", f"[green]✓ Added allowed directory: {result.get('path')}[/green]"))
else:
    self.messages.append(("agent", f"[red]Error: {result.get('message')}[/red]"))
```

**Reason:** `ClientSession.add_allowed_dir()` returns a status dict, not an async generator. Response formatting is done in the TUI directly.

#### `/server` Commands
**Before:**
```python
async for message in self.session.handle_server_command(parts[1] if len(parts) > 1 else None):
    self.messages.append(("agent", self._format_status_message(message)))
```

**After:**
```python
if self.session.start_server():
    self.messages.append(("agent", "[green]✓ Agent server started[/green]"))
else:
    self.messages.append(("agent", "[red]✗ Failed to start agent server[/red]"))
```

**Reason:** `ClientSession` has direct methods (`start_server()`, `stop_server()`, `restart_server()`, `is_server_running()`, `get_server_pid()`). No async generators needed here.

#### `/clear` Command
**Before:**
```python
self.messages.clear()
if self.session.agent_client:
    self.session.agent_client.clear_history()
```

**After:**
```python
self.messages.clear()
self.session.clear_history()
```

**Reason:** Call `ClientSession.clear_history()` directly; no need to check for agent_client existence.

### 4. Main.py Enhancement
**Before:** Only supported standard CLI

**After:**
```python
use_tui = "--tui" in sys.argv

if use_tui:
    editor = GlodTUIEditor(project_root=Path.cwd())
    asyncio.run(editor.run())
else:
    cli = CLI()
    asyncio.run(cli.run_interactive())
```

**Reason:** Provides easy way to launch TUI: `python -m glod --tui`

### 5. Session Initialization
**Before:** Assumed agent_client was always initialized

**After:**
```python
if not await self.session.initialize():
    self.console.print("[red]✗ Failed to initialize agent server[/red]")
    return
```

**Reason:** Properly handles server startup failure cases.

## Architecture Benefits

1. **Separation of Concerns**
   - Business logic: `ClientSession` + `AgentClient`
   - Presentation: `GlodTUIEditor` + Rich formatting
   - CLI & TUI are interchangeable presentation layers

2. **No Direct AgentClient Usage**
   - TUI never imports or accesses `AgentClient`
   - All communication through `ClientSession`
   - Decouples presentation from HTTP details

3. **Proper Event Handling**
   - `StreamEvent` objects carry type information
   - TUI can handle tool phases, errors, chunks separately
   - Extensible for future event types

4. **Simplified Command Logic**
   - Synchronous methods for server control
   - Dict-based responses for add_allowed_dir
   - Consistent error handling pattern

## Testing Recommendations

1. Launch TUI: `python src/main.py --tui`
2. Test message streaming with live updates
3. Test all `/server` commands
4. Test `/allow` with valid/invalid paths
5. Test `/clear` to verify history sync
6. Verify status bar updates correctly

## Files Modified

- `src/tui_editor.py` - Complete refactor to use ClientSession correctly
- `src/main.py` - Added --tui flag support
- `.glod/tui.md` - Updated documentation with correct API usage

## Commit

```
commit 2d52467
refactor: TUI now correctly uses client library

- Fix import: change `client_lib` to `client` (ClientSession, StreamEvent, EventType)
- Replace incorrect `agent_client.stream_run()` with `session.send_prompt_stream()`
- Use ClientSession methods directly for all operations
- Handle StreamEvent objects properly
- Refactor command handlers to use synchronous methods
- Add --tui flag support to main.py
- Update .glod/tui.md documentation
```

