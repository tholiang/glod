# Server Module

This module contains server-side utilities and toolsets that support the agent server.

## Structure

```
src/server/
├── __init__.py
├── glod_api.py      # Library for reading .glod metadata
├── tools/           # Toolsets for the agent
│   ├── __init__.py
│   └── glod_tools.py # GLOD metadata tools
└── README.md        # This file
```

## Components

### glod_api.py

**Purpose**: Generic interface for reading and interacting with `.glod` project metadata.

**Main Class**: `GlodAPI`

**Key Methods**:
- `get_overview()` - Read `overview.md`
- `get_config()` - Read `config.json`
- `get_project_info()` - Get comprehensive project metadata
- `list_custom_tools()` - List custom tools in `.glod/tools/`
- `get_custom_tool_info()` - Get docstring from custom tool
- `get_file_content()` - Read any file in the project
- `save_metadata()` - Save JSON metadata to `.glod/`

**Helper Function**: `create_glod_structure()`
- Creates the `.glod` directory structure for a new project

**Usage**:
```python
from src.server.glod_api import GlodAPI

api = GlodAPI()  # Auto-finds project root by looking for .glod/

# Read project overview
overview = api.get_overview()

# Get all project info
info = api.get_project_info()

# List custom tools
tools = api.list_custom_tools()

# Save analysis results
api.save_metadata({"analysis": "results"}, "analysis.json")
```

### tools/glod_tools.py

**Purpose**: Toolset exposing `.glod` functionality to the coding agent.

**Main Class**: `GlodTools`

**Available Tools**:
- `get_project_overview()` - Get project overview
- `get_project_config()` - Get configuration
- `list_available_tools()` - Discover custom tools
- `get_full_project_info()` - Get complete metadata
- `get_file_from_project()` - Read project files
- `save_project_metadata()` - Save results to `.glod/`
- `get_project_structure_info()` - Extract structure info

**Usage**:
```python
from src.server.tools.glod_tools import GlodTools

tools = GlodTools()

# Get overview
overview = tools.get_project_overview()

# List tools
available = tools.list_available_tools()

# Save analysis
tools.save_project_metadata(
    {"findings": "analysis results"},
    "agent_analysis.json"
)
```

## .glod Structure

The `.glod` folder is a generic metadata system for any project. It contains:

```
.glod/
├── overview.md           # Project overview (required)
├── config.json          # Project config (optional)
├── tools/               # Custom project tools (optional)
│   ├── __init__.py
│   ├── custom_tool1.py
│   └── custom_tool2.py
└── metadata/            # Generated metadata (optional)
    ├── analysis.json
    └── ...
```

### overview.md

High-level project information:
- Project name and description
- Architecture overview
- Technology stack
- Project structure
- Key files and their purposes
- How to run the project
- Development guidelines

### config.json

Machine-readable configuration:
- Project settings
- Tool configurations
- Agent instructions
- Custom parameters

### tools/

Custom Python tools specific to this project. Each tool should:
- Have a clear docstring
- Be a Python module
- Provide utility functions for the agent

## Integration with Agent

These tools can be integrated into the agent server's tool set:

```python
from src.server.tools.glod_tools import GlodTools

# In agent_server.py
glod_tools = GlodTools()

# Add methods to agent's available tools
# agent.tools.append(glod_tools.get_project_overview)
# agent.tools.append(glod_tools.list_available_tools)
# etc.
```

## Extending .glod

To add new metadata to `.glod`:

1. **For overview changes**: Edit `.glod/overview.md` directly
2. **For configuration**: Create/update `.glod/config.json` with JSON structure
3. **For custom tools**: Add Python files to `.glod/tools/`
4. **For results**: Use `api.save_metadata()` to save JSON files

## Generic Design

The `GlodAPI` and `GlodTools` classes are completely generic and work with any project that has a `.glod` structure. No project-specific code is needed:

- `GlodAPI` auto-discovers the project root
- `get_config()` works with any JSON structure
- `list_custom_tools()` discovers any `.py` files
- Methods are idempotent and handle missing files gracefully

This makes `.glod` a portable, reusable metadata system for any codebase.

## Example: Creating .glod for a Project

Run the setup script in the project root:

```bash
python setup_glod.py
```

This creates:
- `.glod/` directory
- `.glod/overview.md` with project info
- `.glod/tools/` directory for custom tools

Then customize:
- Edit `.glod/overview.md` with your project details
- Add `.glod/config.json` with configuration
- Add custom tools to `.glod/tools/`

## Testing

```python
# Test GlodAPI
from src.server.glod_api import GlodAPI

api = GlodAPI()
overview = api.get_overview()
assert overview is not None

# Test GlodTools
from src.server.tools.glod_tools import GlodTools

tools = GlodTools()
info = tools.get_project_overview()
assert len(info) > 0
```

