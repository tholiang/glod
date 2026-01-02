# Agent Streaming

Agent runs on FastAPI server, streams responses as Server-Sent Events (SSE).

## Message History Format

Message history is serialized using `ModelMessagesTypeAdapter` from pydantic-ai:
- Empty history: empty string `""`
- Non-empty: JSON bytes decoded to UTF-8 string
- Deserialization validates against Pydantic model for tagged union `list[ModelRequest|ModelResponse]`
- Server is stateless; all history managed client-side and round-tripped in requests/responses

- `"chunk"` - Response text segments (PartStartEvent, PartDeltaEvent)
- `"tool_call"` - Tool invocation: `tool_name(args)` (FunctionToolCallEvent)
- `"tool_result"` - Tool execution result (FunctionToolResultEvent)
- `"complete"` - Stream complete, content is serialized message history
- `"error"` - Error occurred

## Server Processing

`_stream_generator()` in `agent_server.py`:
1. Calls `editor_run_stream()` to get event tuples
2. Wraps each tuple in `StreamEvent(type=event_type, content=content)`
3. Converts to SSE format: `data: {json}\n\n`
4. Sends completion event with updated message history

## Client Processing

`run_stream()` in `client_agent.py` parses SSE stream:
1. Splits by `data: ` prefix
2. Deserializes JSON event data
3. Calls registered callbacks:
   - `on_tool_phase_start()` when first tool event received
   - `on_tool_call(content)` for each tool invocation
   - `on_tool_result(content)` for each tool result
   - `on_tool_phase_end()` when non-tool chunks resume
   - `on_chunk(content)` for final response text
4. Updates message history on completion event

## Key Design

- Server is stateless; all message history managed client-side
- Tool calls/results are distinct event types, not plaintext chunks
- Proper event type allows CLI to render tool activity with distinct styling

