# GLOD: AI Code Editor

Client-server AI code editor. Agent runs on FastAPI (port 8000), client communicates via HTTP RPC. Message history stored client-side.

## Components
- **Client** (`src/main.py`) - CLI, message history, user interaction
- **Client Library** (`src/client_lib.py`) - Rich formatting utilities for console output
- **HTTP Client** (`src/client_agent.py`) - Async HTTP communication to agent
- **Server Manager** (`src/server_manager.py`) - Subprocess manager for agent
- **Agent Server** (`src/server/agent_server.py`) - FastAPI + Pydantic AI + Claude (to implement)
- **Agent Server** (`src/server/agent_server.py`) - FastAPI + Pydantic AI + Claude (to implement)

## Message Flow

```
CLI prompt → Client HTTP POST → Agent (stateless) → Claude → Response
  ↓
Message history updated and stored locally
```

## Agent Server Endpoints

- `GET /health` - Health check
- `POST /run` - Execute prompt, return response + updated history
- `POST /run-stream` - Stream response via Server-Sent Events
- `POST /add-allowed-dir` - Add file access directory

Request format: `{prompt: str, message_history: str}`

## Tech Stack

- Python 3.8+, FastAPI, Pydantic AI, Claude 3.5 Sonnet, httpx
- Streaming via Server-Sent Events
- Port: 8000

## Key Implementation Notes

- Agent is stateless; all history on client
- Runs from `src/` directory
- HTTP timeout: 300s
- API key in `anthropic_api_key.txt`

