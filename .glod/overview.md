# GLOD - AI Code Editor

AI-assisted code editor with an agent server that understands projects through the `.glod` project metadata infrastructure.

## What Does This Project Do?

GLOD is a client-server application that uses an AI agent to help with code editing and understanding. The system is built around a `.glod` metadata directory that gives the agent context about any project it's working on.

## Architecture

```
Client → HTTP → Agent Server → AI Model
                       ↓
                 .glod/ (Project Context)
```

### Components

1. **Client** (`src/main.py`, `src/client_agent.py`)
   - HTTP client for communicating with agent server
   - Sends code editing requests

2. **Agent Server** (`src/agents/agent_server.py`)
   - FastAPI server running the AI agent
   - Uses Pydantic AI framework
   - Integrates with Claude via Anthropic API

3. **.glod Infrastructure** (`src/server/`)
   - `glod_api.py`: Low-level .glod access library
   - `tools/glod_tools.py`: Agent-friendly tools for project metadata

## Technology Stack

- **Language**: Python 3.8+
- **Framework**: FastAPI (server), Pydantic AI (agent)
- **AI Model**: Claude 3.5 Sonnet (via Anthropic)
- **Communication**: HTTP/REST
- **Project Context**: .glod metadata system

## Project Structure

```
src/
├── main.py                    # Client application
├── client_agent.py            # HTTP client for agent
├── server/                    # ✨ Server utilities
│   ├── glod_api.py           # .glod access library
│   ├── tools/
│   │   └── glod_tools.py     # Agent tools for .glod
│   └── README.md
├── agents/
│   └── agent_server.py       # FastAPI agent server
└── tools/
    ├── files.py              # File manipulation tools
    └── ...

.glod/                         # Project metadata
├── overview.md               # This file
├── config.json              # Configuration (optional)
└── tools/                   # Custom tools (optional)
```

## Key Files

- **`src/server/glod_api.py`**: Core .glod access library
- **`src/server/tools/glod.py`**: Agent-friendly tools
- **`src/agents/agent_server.py`**: Main agent server

## How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up .glod Infrastructure
```bash
python setup_glod.py
python test_glod_setup.py
```

### 3. Run Agent Server
```bash
python -m uvicorn src.agents.agent_server:app --reload
```

### 4. Run Client (in another terminal)
```bash
python src/main.py
```

## Development Guidelines

### Code Style
- Follow PEP 8
- Use type hints
- Add docstrings to functions

### Project Context
- Update `.glod/overview.md` when project changes
- Use `GlodTools` in agent server for project awareness
- Custom tools can be added to `.glod/tools/`

### Testing
- Run `python test_glod_setup.py` to verify .glod setup
- Write tests for new features

## .glod Infrastructure

The `.glod` folder is a **generic metadata system** that lets the AI agent understand any project:

```
.glod/
├── overview.md           # Project overview (this file)
├── config.json          # Machine-readable config (optional)
└── tools/               # Custom analysis tools (optional)
```

### Usage in Agent

```python
from src.server.tools.glod_tools import GlodTools

tools = GlodTools()
overview = tools.get_project_overview()  # Reads this file
config = tools.get_project_config()
available = tools.list_available_tools()
```

## Integration with Agent

The agent has access to `.glod` information through `GlodTools`:

```python
@app.post("/run")
async def run_agent(request: Request):
    glod_tools = GlodTools()
    
    # Get project context
    overview = glod_tools.get_project_overview()
    
    # Use in system prompt
    system_prompt = f"You're working on:\n{overview}"
    
    # Agent now understands the project!
    response = await agent.run(request.prompt, system_prompt=system_prompt)
    return response
```

## Important Directories

- **`src/`**: Source code
- **`src/server/`**: Server utilities including .glod infrastructure
- **`src/agents/`**: Agent server implementation
- **`.glod/`**: Project metadata for the agent
- **`docs/`**: Documentation

## Resources

- **Quick Start**: `docs/GLOD_QUICKSTART.md`
- **Implementation Guide**: `docs/impl/glod.md`
- **Infrastructure Docs**: `docs/GLOD_INFRASTRUCTURE.md`
- **API Reference**: `src/server/README.md`

## Support

For help with .glod infrastructure:
- See `docs/impl/glod.md` for implementation details
- See `docs/GLOD_QUICKSTART.md` for quick setup
- See `test_glod_setup.py` for example usage
