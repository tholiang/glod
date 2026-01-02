# GLOD - AI Code Editor

A client-server AI code editor where you interact with an AI assistant to edit code. The agent runs as a separate FastAPI server (HTTP RPC), client communicates via REST API. Message history is stored client-side, making the agent stateless and restartable.

(largely made by itself)

## Quick Start

### Prerequisites
```bash
pip install -r requirements.txt
```

### Terminal 1: Start Agent Server
```bash
python main.py /server start
```

You should see:
```
✅ Server started on http://127.0.0.1:8000
```

### Terminal 2: Start Client
```bash
python main.py
```

You should see:
```
✅ Connected to agent server!
Type /help for commands.

>
```

### Example Usage
```
> Add a docstring to the Client class in main.py
[Agent processes and responds...]

> Show me the file tools available
[Agent lists the tools...]

> /allow /path/to/directory
Directory added to allowlist

> /clear
Message history cleared.

## Key Features

✅ **HTTP RPC** - Clean REST API instead of subprocess communication  
✅ **Client-Side History** - Message history stays with the client  
✅ **Stateless Agent** - Kill and restart anytime without losing context  
✅ **Client-Side Allowlist** - Directory access managed and validated on client  
✅ **Easy to Test** - Use curl or Swagger UI at `http://127.0.0.1:8000/docs`  
✅ **Type-Safe** - Proper use of pydantic-ai and type hints  
✅ **Extensible** - Add new endpoints easily  
✅ **Streaming** - Real-time response streaming via Server-Sent Events

## File Structure

```
glod/
├── src/
│   ├── main.py                 # CLI client
│   ├── client_agent.py         # HTTP client wrapper
│   ├── client_lib.py           # Rich formatting utilities
│   ├── server_manager.py       # Subprocess manager for server
│   ├── server/
│   │   ├── agent_server.py     # FastAPI server
│   │   └── agents/
│   │       └── editor.py       # Agent implementation
│   └── tools/
│       └── files.py            # File manipulation tools
├── .glod/                      # Agent documentation
│   ├── overview.md
│   ├── cli.md
│   ├── agent_streaming.md
│   ├── client_lib.md
│   └── subagents.md
├── requirements.txt
├── readme.md
└── setup.py
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

## Testing the Agent

While the server is running:

```bash
## Development

### Adding a New Agent Endpoint

1. Add endpoint in `src/server/agent_server.py`:
```python
@server.post("/new-endpoint")
async def new_endpoint(request: MyRequest) -> MyResponse:
    # Your code here
    return MyResponse(...)
```

2. Add client method in `src/client_agent.py`:
```python
async def new_method(self, data: str) -> dict:
    response = await self.client.post(f"{self.base_url}/new-endpoint", json={...})
    return response.json()
```

### Adding a New Tool

1. Create tool function in `src/tools/files.py` with proper type hints
2. Register in agent via `@tool` decorator in `src/server/agents/editor.py`
3. Tool will be available in agent context automatically

### Running with Auto-Reload

```bash
# Start client (auto-connects to server)
python main.py

# In another terminal, restart server with changes
python main.py /server restart
```

## Troubleshooting

**"Could not connect to agent server"**
- Start the server: `python main.py /server start`

**"Server returned 500"**
- Check the server logs in the terminal where it's running

**Agent crashed**
- Restart it: `python main.py /server restart`
- Message history is preserved on the client

**Want to see API docs**
- Open `http://127.0.0.1:8000/docs` while server is running

## Project Root

The client uses the current working directory (CWD) as the project root for file operations. Start the client from your project directory:

```bash
cd /path/to/your/project
python /path/to/glod/src/main.py
```

## Documentation

- **[.glod/overview.md](.glod/overview.md)** - Architecture and components
- **[.glod/cli.md](.glod/cli.md)** - CLI interface details
- **[.glod/agent_streaming.md](.glod/agent_streaming.md)** - Streaming implementation
- **[.glod/client_lib.md](.glod/client_lib.md)** - Client library utilities

## License

MIT
6. **Client** displays output and stores it in local message history

Key insight: The agent is **completely stateless**. All conversation history is maintained on the client side. This allows you to:
- Restart the agent anytime (`python -m agents.agent_server`)
- Update the agent code and restart without losing context
- Scale to multiple agents
- Move the agent to a different machine

## Development

### Adding a New Agent Endpoint

1. Add endpoint in `agents/agent_server.py`:
```python
@app.post("/new-endpoint")
async def new_endpoint(request: MyRequest) -> MyResponse:
    # Your code here
    return MyResponse(...)
```

2. Add client method in `client_agent.py`:
```python
async def new_method(self, data: str) -> dict:
    response = await self.client.post(f"{self.base_url}/new-endpoint", json={...})
    return response.json()
```

### Running with Reload
```bash
python -m agents.agent_server --reload
```

## Troubleshooting

**"Could not connect to agent server"**
- Start the agent: `python -m agents.agent_server`

**"Server returned 500"**
- Check the agent server terminal for error messages

**Agent crashed**
- Restart it: `python -m agents.agent_server`

**Want to see API docs**
- Open `http://127.0.0.1:8000/docs` while server is running

## Future Enhancements

- Add message history persistence to disk
- Add authentication to the agent server
- Run multiple agent instances
- Deploy agent to cloud
- Build a web UI
- Add streaming responses
- Add function calling for complex tools

## License

MIT

coding agent

see `docs/`