# GLOD: AI Code Editor

Client-server AI code editor. Agent runs on FastAPI (port 8000), client communicates via HTTP RPC. Message history stored client-side.

## Components
- **Entry Point** (`src/main.py`) - Initializes CLI and runs interactive loop
- **CLI Handler** (`src/cli.py`) - User interaction and output presentation (Rich formatting)
- **Client Session** (`src/client/session.py`) - Session management, server lifecycle, command routing
- **Agent Client** (`src/client/agent_client.py`) - HTTP RPC to agent, yields StreamEvent objects (no output handling)
- **Server Manager** (`src/server_manager.py`) - Subprocess manager for agent (uses CWD as project root)
- **Agent Server** (`src/server/agent_server.py`) - FastAPI + Pydantic AI + Claude

## Message Flow

```
User Input → CLI (presentation) → ClientSession (business logic) → AgentClient (HTTP) → Agent → Claude
                                           ↓
                                   Message history
```

## Architecture

**Client logic is separated into layers:**
- **Business Logic** (`src/client/`) - Pure Python, no I/O, returns data/streams
- **CLI Presentation** (`src/cli.py`) - Handles output formatting and user interaction
- **Entry Point** (`src/main.py`) - Bootstraps CLI

**AgentClient** yields `StreamEvent` objects instead of printing:
- `EventType.TOOL_CALL`, `TOOL_RESULT`, `CHUNK`, `COMPLETE`, `ERROR`
- `TOOL_PHASE_START` and `TOOL_PHASE_END` emitted by client for formatting control
- Callers handle presentation via event dispatch

## Agent Server Endpoints

- `GET /health` - Health check
- `POST /run` - Execute prompt, return response
- `POST /run-stream` - Stream response via Server-Sent Events
- `POST /add-allowed-dir` - Register allowed directory with agent

Request format: `{prompt: str, message_history: str}`

## Tech Stack

- Python 3.8+, FastAPI, Pydantic AI, Claude 3.5 Sonnet, httpx
- Streaming via Server-Sent Events
- Rich console library for formatting
- Port: 8000

## Key Implementation Notes

- Agent is stateless; all history on client
- Directory allowlist validated client-side before sending to agent
- HTTP timeout: 300s
- API key in `anthropic_api_key.txt`
- Runs from `src/` directory

- Agent is stateless; all history on client
- Runs from `src/` directory
- HTTP timeout: 300s
- API key in `anthropic_api_key.txt`

