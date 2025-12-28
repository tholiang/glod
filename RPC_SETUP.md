# Agent RPC Server Setup

## Overview

The agent now runs as a separate **HTTP RPC server**, which is much cleaner than subprocess communication!

```
┌──────────────────┐
│  Client (main)   │  Keeps message history
│  HTTP requests   │
└────────┬─────────┘
         │
    HTTP │ POST /run
         │ {"prompt": "..."}
         ▼
┌──────────────────┐
│ Agent Server     │  Stateless
│ (FastAPI)        │  Can restart anytime
└──────────────────┘
```

## Quick Start

### Terminal 1: Start the Agent Server

```bash
cd /Users/thomasliang/Documents/Programs/glod/src
python -m agents.agent_server
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Terminal 2: Run the Client

```bash
cd /Users/thomasliang/Documents/Programs/glod/src
python main.py
```

You should see:
```
✅ Connected to agent server!
Type /help for commands.

> Tell me to edit a file
[Agent responds...]
```

## Why This is Better

### Before (subprocess with stdin/stdout)
- ❌ Complex JSON line protocol
- ❌ Hard to debug
- ❌ Hard to add features

### After (HTTP RPC)
- ✅ Standard REST API
- ✅ Easy to test with curl
- ✅ Easy to add endpoints
- ✅ Can restart agent freely
- ✅ Can run agent on different machine
- ✅ Built-in Swagger docs

## Testing the Agent Server

While it's running, you can test it directly:

```bash
# Test health
curl http://127.0.0.1:8000/health

# Test running a prompt
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Say hello"}'

# View API docs
# Open http://127.0.0.1:8000/docs in your browser
```

## Commands in Client

```
> Your prompt here
[Agent processes and responds]

> /clear
[Clear message history]

> /help
[Show help]

> /exit
[Exit the program]
```

## Architecture

### Agent Server (`agents/agent_server.py`)
- FastAPI application
- Listens on `http://127.0.0.1:8000`
- Endpoints:
  - `POST /run` - Process a prompt
  - `GET /health` - Health check
  - `GET /docs` - Swagger UI
- Completely stateless
- Can be killed and restarted anytime

### Client (`main.py`)
- HTTP client for the agent server
- Maintains message history
- Handles user input
- `AgentClient` class handles HTTP communication

### HTTP Client (`client_agent.py`)
- `AgentClient` class
- Simple async HTTP client using httpx
- Handles connection errors gracefully
- Provides methods:
  - `health_check()` - Check if server is running
  - `run(prompt, message_history)` - Send prompt to agent
  - `close()` - Clean up

## Adding New Endpoints

Want to add more endpoints to the agent server? It's easy!

```python
# In agents/agent_server.py

@app.post("/some-new-endpoint")
async def some_new_endpoint(request: SomeRequest) -> SomeResponse:
    """Your new endpoint"""
    # Your code here
    return SomeResponse(...)

# Then in client_agent.py, add a method:

async def some_new_method(self) -> dict:
    response = await self.client.post(
        f"{self.base_url}/some-new-endpoint",
        json={...}
    )
    return response.json()
```

## Configuration

Agent server runs on `127.0.0.1:8000` by default.

To change, edit `agents/agent_server.py`:

```python
if __name__ == "__main__":
    uvicorn.run(
        "agents.agent_server:app",
        host="127.0.0.1",  # Change this
        port=8000,         # Change this
        reload=False
    )
```

And update client in `client_agent.py`:

```python
def __init__(self, base_url: str = "http://127.0.0.1:8000"):
    # Change the default here
```

## Troubleshooting

### "Could not connect to agent server"
- Is the agent server running? Start it in Terminal 1
- Is it on the right port? Check your configuration

### "Server returned 500"
- There's an error in the agent. Check the agent server terminal for the error

### Want to see the API docs?
- Open http://127.0.0.1:8000/docs in your browser while the server is running

## Next Steps

Now that you have a proper RPC interface, you can:

1. **Add more endpoints** - Add features without modifying the protocol
2. **Run agent on different machine** - Just change the base_url
3. **Multiple agent instances** - Run multiple servers on different ports
4. **Build a web UI** - Frontend can talk directly to the agent server
5. **Add authentication** - Add API keys to endpoints
6. **Persistent storage** - Save message history to a database

The architecture is now truly scalable! 🎉

