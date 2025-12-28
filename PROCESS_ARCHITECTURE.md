# Process Architecture: Client-Server Separation

## Overview

The client and agent now run in **separate processes**:

```
┌─────────────────────────────┐
│   CLIENT (main.py)          │
│  - Message history          │
│  - User interaction loop     │
│  - Session state            │
└──────────────┬──────────────┘
               │ JSON messages
               │ (stdin/stdout)
┌──────────────▼──────────────┐
│  AGENT SERVER (agent_...)   │
│  - Stateless processing     │
│  - Tool execution           │
│  - Can be killed/restarted  │
└─────────────────────────────┘
```

## How to Use

### Normal Usage
```
> Tell me to edit a file
[Agent processes and responds]

> Make another change
[Message history preserved, agent still has context]
```

### Restart Agent Without Losing History
```
> /restart
[Agent process killed and restarted]
[All previous messages are still in client memory]

> Continue the conversation
[Agent uses full history to understand context]
```

### Clear History
```
> /clear
[Conversation history cleared, start fresh]
```

### Stop Agent Temporarily
```
> /stop
[Agent process stopped]
> /restart
[Agent back online]
```

## Key Commands

| Command | Effect |
|---------|--------|
| `/restart` | Kill and restart the agent subprocess |
| `/stop` | Kill the agent (you can restart later) |
| `/clear` | Clear conversation history |
| `/exit` | Exit the program |
| `/help` | Show all commands |

## Implementation Details

### Files

1. **`main.py`** - Client (this process)
   - `Client` class: Manages message history
   - User input loop
   - Commands handler

2. **`client_agent.py`** - Client-side agent wrapper
   - `ProcessAgent` class: Manages subprocess
   - Handles stdin/stdout communication
   - Provides methods to start/stop/restart agent

3. **`agents/agent_server.py`** - Agent server (subprocess)
   - Reads JSON requests from stdin
   - Processes them asynchronously
   - Writes JSON responses to stdout
   - Completely stateless

### Communication Protocol

**Client → Agent (JSON on stdin):**
```json
{
  "prompt": "Edit this file",
  "message_history": [
    {"type": "user", "content": "..."},
    {"type": "assistant", "content": "..."}
  ]
}
```

**Agent → Client (JSON on stdout):**
```json
{
  "status": "success",
  "output": "I edited the file",
  "new_messages": [
    {"type": "assistant", "content": "..."}
  ]
}
```

## Future Improvements

### Option 1: Socket-based (Better for remote agents)
Replace stdin/stdout with TCP sockets to run agent on different machine

### Option 2: True Streaming
Modify `agent_server.py` to send intermediate events (tool calls, thinking, etc.) 
so they can be displayed in real-time while processing

### Option 3: Message Queue
Use Redis/RabbitMQ for more robust message passing and multiple agent instances

### Option 4: HTTP API
Turn agent into a FastAPI service and use HTTP requests
```
POST /api/agent/process
{
  "prompt": "...",
  "message_history": [...]
}
```

## Troubleshooting

**"Agent process died"**
- Agent subprocess crashed
- Use `/restart` to restart it

**"Communication error"**
- JSON serialization issue
- Check agent logs (stderr)

**Message history not persisting**
- History is in client memory only
- Will be lost if client process exits
- (Future: Add save/load to persistent storage)

