# Quick Start Guide

## Two Terminal Setup

### Terminal 1: Start Agent Server
```bash
cd /Users/thomasliang/Documents/Programs/glod/src
python -m agents.agent_server
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Terminal 2: Start Client
```bash
cd /Users/thomasliang/Documents/Programs/glod/src
python main.py
```

Expected output:
```
✅ Connected to agent server!
Type /help for commands.

>
```

## Using the Client

### Basic Usage
```
> Edit src/main.py to add a docstring to the Client class
[Agent processes and responds...]

> Make the changes you suggested
[Agent responds again...]
```

### Clear History
```
> /clear
Message history cleared.
```

### Get Help
```
> /help
Available commands:
  /exit      - Exit the program
  /clear     - Clear message history
  /help      - Show this help message
...
```

### Exit
```
> /exit
[Program exits]
```

## Testing the Agent Server Directly

While the server is running, test it with curl:

```bash
# Health check
curl http://127.0.0.1:8000/health

# Run a prompt
curl -X POST http://127.0.0.1:8000/run \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Say hello"}'
```

## View Interactive API Docs

While agent server is running, open in browser:
```
http://127.0.0.1:8000/docs
```

You'll see:
- All available endpoints
- Request/response schemas
- Interactive "Try it out" button for each endpoint

## File Structure

```
src/
├── main.py                    # Client (message history, user interaction)
├── client_agent.py            # HTTP client (talks to agent server)
└── agents/
    └── agent_server.py        # Agent (stateless, HTTP server)
```

## What Just Changed

✅ **Old**: Subprocess communication with JSON lines  
✅ **New**: HTTP RPC with FastAPI

**Better because**:
- Much cleaner to work with
- Easy to test (curl, Swagger)
- Easy to extend (add endpoints)
- Can restart agent anytime
- Professional architecture

## Dependencies

Make sure you have:
```bash
pip install fastapi uvicorn httpx pydantic-ai anthropic
```

## Troubleshooting

### "Could not connect to agent server"
- Is Terminal 1 running the agent? Start it with: `python -m agents.agent_server`

### "Server returned 500"
- There's an error in the agent. Check Terminal 1 output for details.

### Agent server crashes
- Check Terminal 1 for error messages
- Restart it with: `python -m agents.agent_server`

### Want to see what's happening?
- Agent logs appear in Terminal 1
- Client logs appear in Terminal 2

## Next Commands to Try

```
> Create a new file called test.py with a simple function
> Edit test.py to add better docstrings
> List all Python files in the src directory
> /clear
> Show me the contents of main.py
```

That's it! You're all set! 🚀

src/
├── main.py                 # Client (runs here, keeps history)
├── client_agent.py        # Subprocess wrapper
└── agents/
    └── agent_server.py    # Agent (runs in subprocess)
```

## If Something Goes Wrong

**"Agent process died"**
```
> /restart
```

**"Agent didn't respond"**
```
> /stop
> /restart
```

**"Want to start fresh?"**
```
> /clear
```

**Want to see what's available?**
```
> /help
```

That's it! You're ready to go! 🚀

