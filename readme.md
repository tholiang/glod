# GLOD - AI Code Editor

A client-agent architecture where you can interact with an AI assistant to edit code, with the agent running as a separate HTTP RPC server.

(in large part made by itself)

## Quick Start

### Prerequisites
```bash
pip install fastapi uvicorn httpx pydantic-ai anthropic
```

### Terminal 1: Start Agent Server
```bash
cd src
python -m agents.agent_server
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2: Start Client
```bash
cd src
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

> /clear
Message history cleared.

> /help
[Shows available commands]
```

## Architecture

```
┌──────────────────────┐
│  Client (main.py)    │  • Message history
│  HTTP requests       │  • User interaction
└──────────┬───────────┘
           │
      HTTP │ REST API
           │
┌──────────▼───────────┐
│  Agent (FastAPI)     │  • Stateless
│  agent_server.py     │  • Can restart anytime
└──────────────────────┘
```

## Key Features

✅ **HTTP RPC** - Clean REST API instead of subprocess communication  
✅ **Client-Side History** - Message history stays with the client  
✅ **Stateless Agent** - Kill and restart anytime without losing context  
✅ **Easy to Test** - Use curl or Swagger UI at `http://127.0.0.1:8000/docs`  
✅ **Type-Safe** - No typing issues, proper use of pydantic-ai  
✅ **Extensible** - Add new endpoints easily  

## Files

| File | Purpose |
|------|---------|
| `src/main.py` | Client application (message history, user input) |
| `src/client_agent.py` | HTTP client for agent communication |
| `src/agents/agent_server.py` | Agent RPC server (FastAPI) |
| `src/tools/files.py` | File manipulation tools for the agent |
| `src/app.py` | App configuration and path allowlist |

## Commands

```
> Your prompt          # Send to agent
> /clear              # Clear conversation history
> /help               # Show this help
> /exit               # Exit program
```

## Testing the Agent

While the server is running:

```bash
# Health check
curl http://127.0.0.1:8000/health

# Run a prompt
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Say hello"}'

# Interactive API docs
# Open http://127.0.0.1:8000/docs in your browser
```

## Documentation

- **[QUICK_START.md](QUICK_START.md)** - Get started in 2 minutes
- **[ARCHITECTURE_FINAL.md](ARCHITECTURE_FINAL.md)** - Full architecture details
- **[RPC_SETUP.md](RPC_SETUP.md)** - RPC server setup and usage

## How It Works

1. **Client** starts and connects to agent server via HTTP
2. **User** types a prompt
3. **Client** sends HTTP POST request to `/run` endpoint
4. **Agent** processes the prompt independently (stateless)
5. **Agent** returns the output via HTTP response
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