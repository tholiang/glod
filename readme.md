# GLOD - AI Code Editor

A client-server AI code editor where you interact with Claude AI to edit code. The agent runs as a FastAPI server (HTTP RPC), client communicates via REST API. Message history is stored client-side, making the agent stateless and restartable.

## Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Terminal 1: Start Agent Server
```bash
python src/main.py /server start
```

You should see:
```
✅ Server started on http://127.0.0.1:8000
```

### Terminal 2: Start Client
```bash
python src/main.py
```

You should see:
```
✅ Connected to agent server!
Type /help for commands.

>
```

## Commands

```
> Your prompt          # Send to agent
> /allow <dir>        # Add directory to allowlist
> /clear              # Clear conversation history
> /help               # Show commands
> /exit               # Exit program
> /server start       # Start agent server
> /server stop        # Stop agent server
> /server status      # Check server status
```

## Key Features

✅ **HTTP RPC** - Clean REST API instead of subprocess communication  
✅ **Client-Side History** - Message history stays with the client  
✅ **Stateless Agent** - Kill and restart anytime without losing context  
✅ **Client-Side Allowlist** - Directory access managed and validated on client  
✅ **Streaming** - Real-time response streaming via Server-Sent Events  
✅ **Type-Safe** - Proper use of pydantic-ai and type hints  
✅ **Easy to Test** - Use curl or Swagger UI at `http://127.0.0.1:8000/docs`

## File Structure

```
glod/
├── src/
│   ├── main.py                      # CLI entrypoint
│   ├── cli.py                       # CLI interface (Rich formatting)
│   ├── server_manager.py            # Subprocess manager for server
│   ├── client/
│   │   ├── agent_client.py          # HTTP RPC client
│   │   └── session.py               # Session management
│   ├── server/
│   │   ├── agent_server.py          # FastAPI server
│   │   ├── agents/
│   │   │   └── editor.py            # Agent implementation
│   │   └── tools/
│   │       ├── files.py             # File manipulation tools
│   │       ├── git.py               # Git tools
│   │       └── agents.py            # Subagent spawning
│   └── util.py                      # Formatting utilities
├── .glod/                           # Agent documentation
│   ├── overview.md                  # Architecture
│   ├── cli.md                       # CLI interface
│   ├── agent_streaming.md           # Streaming implementation
│   └── subagents.md                 # Subagent spawning
├── requirements.txt
├── readme.md
└── setup.py
```

## Project Root

The client uses the current working directory (CWD) as the project root for file operations. Start the client from your project directory:

```bash
cd /path/to/your/project
python /path/to/glod/src/main.py
```

## Development

### Adding a New Agent Tool

1. Create tool function in `src/server/tools/` with proper type hints
2. Register via `@tool` decorator in `src/server/agents/editor.py`
3. Tool will be available in agent context automatically

### Adding a New Agent Endpoint

1. Add endpoint in `src/server/agent_server.py`:
```python
@server.post("/new-endpoint")
async def new_endpoint(request: MyRequest) -> MyResponse:
    return MyResponse(...)
```

2. Add client method in `src/client/agent_client.py`:
```python
async def new_method(self, data: str) -> dict:
    response = await self.client.post(f"{self.base_url}/new-endpoint", json={...})
    return response.json()
```

## Troubleshooting

**"Could not connect to agent server"**
- Start the server: `python src/main.py /server start`

**"Server returned 500"**
- Check the server logs in the terminal where it's running

**Agent crashed**
- Restart it: `python src/main.py /server restart`
- Message history is preserved on the client

**Want to see API docs**
- Open `http://127.0.0.1:8000/docs` while server is running

## Documentation

- **[.glod/overview.md](.glod/overview.md)** - Architecture and components
- **[.glod/cli.md](.glod/cli.md)** - CLI interface details
- **[.glod/agent_streaming.md](.glod/agent_streaming.md)** - Streaming implementation
- **[.glod/subagents.md](.glod/subagents.md)** - Subagent spawning

## License

MIT
see `docs/`