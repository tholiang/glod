# .glod Infrastructure Documentation

## Overview

`.glod` is a **generic, project-agnostic metadata system** that enables the coding agent to understand any project it's working on. It provides a standardized way to store project information, configuration, and custom toolsets.

## Purpose

The agent needs context about projects to work effectively. Instead of hardcoding project-specific logic, `.glod` provides:

1. **Project Understanding** - What does this project do?
2. **Architecture Context** - How is it structured?
3. **Configuration** - What are the settings?
4. **Custom Tools** - What project-specific tools exist?
5. **Metadata** - Results of analysis and findings

## Design Philosophy

- **Generic**: Works with any project, no customization needed
- **Portable**: Can be copied to any repository
- **Extensible**: Easy to add more metadata
- **Version-Controlled**: Lives in the repository
- **Human-Readable**: Markdown and JSON, easy to edit

## Directory Structure

```
.glod/
├── overview.md                  # Project overview (REQUIRED)
├── config.json                  # Configuration (OPTIONAL)
├── tools/                       # Custom tools (OPTIONAL)
│   ├── __init__.py
│   ├── analysis_tool.py
│   └── validation_tool.py
└── metadata/                    # Generated metadata (OPTIONAL)
    ├── analysis.json
    ├── findings.json
    └── cache.json
```

## Core Components

### 1. overview.md (Required)

The main project documentation that provides human-readable context.

**Contents**:
```markdown
# Project Name

## Project Summary
- What is this project?
- What does it do?

## Architecture
- How is it structured?
- Key components

## Technology Stack
- Languages, frameworks, libraries

## Project Structure
- Directory organization
- Key files

## How It Works
- Process overview
- Key concepts

## Key Files
- Important files and their purposes

## Getting Started
- How to run the project

## Development
- How to develop
- Testing approach
```

**Example**: See `.glod/overview.md` in this project

**Agent Usage**:
```python
overview = glod_api.get_overview()
# Agent reads and understands project context
```

### 2. config.json (Optional)

Machine-readable configuration for the project.

**Example Structure**:
```json
{
  "project_name": "GLOD",
  "description": "AI Code Editor",
  "type": "application",
  "language": "python",
  "version": "0.1.0",
  "main_entry": "src/main.py",
  "server_entry": "src/agents/agent_server.py",
  "directories": {
    "src": "Source code",
    "tests": "Test files",
    "docs": "Documentation"
  },
  "dependencies": {
    "fastapi": ">=0.128.0",
    "pydantic-ai": ">=1.39.0"
  },
  "agent_instructions": {
    "file_editing": "Always add docstrings",
    "code_style": "Follow PEP 8",
    "testing": "Write tests for new features"
  }
}
```

**Agent Usage**:
```python
config = glod_api.get_config()
# Agent uses config for:
# - Understanding project type
# - Finding entry points
# - Following project conventions
# - Respecting custom instructions
```

### 3. tools/ Directory (Optional)

Custom Python tools specific to this project.

**Purpose**: Extend agent capabilities with project-specific functionality

**Example Tool**:
```python
# .glod/tools/code_analysis.py
"""
Code analysis tools for this project.

Provides specialized analysis for the specific architecture of this project.
"""

def analyze_architecture():
    """Analyze the project's architecture."""
    pass

def find_related_files(file_path):
    """Find files related to a given file."""
    pass
```

**Agent Usage**:
```python
# Agent discovers and loads custom tools
tools = glod_api.list_custom_tools()  # ['code_analysis', 'validation']

# Agent can import and use them
from .glod.tools import code_analysis
results = code_analysis.analyze_architecture()
```

### 4. metadata/ Directory (Optional)

Generated metadata and cached analysis results.

**Contents**:
- `analysis.json` - Agent analysis results
- `findings.json` - Code quality findings
- `cache.json` - Cached project info
- Custom metadata files

**Agent Usage**:
```python
# Agent saves findings back to .glod/
api.save_metadata(
    {"issues": [...], "recommendations": [...]},
    "analysis.json"
)
```

## API Reference

### GlodAPI Class

Located in `src/server/glod_api.py`

```python
from src.server.glod_api import GlodAPI

# Initialize (auto-finds project root)
api = GlodAPI()

# Or specify project root
api = GlodAPI(project_root=Path("/path/to/project"))
```

**Methods**:

| Method | Returns | Purpose |
|--------|---------|---------|
| `get_overview()` | `str \| None` | Read overview.md |
| `get_config()` | `dict \| None` | Read config.json |
| `get_project_info()` | `dict` | Get all metadata |
| `list_custom_tools()` | `list[str]` | List custom tools |
| `get_custom_tool_info(name)` | `str \| None` | Get tool docstring |
| `get_file_content(path)` | `str \| None` | Read project file |
| `save_metadata(data, filename)` | `bool` | Save to .glod/ |

### GlodTools Class

Located in `src/server/tools/glod_tools.py`

Wraps `GlodAPI` with agent-friendly methods:

```python
from src.server.tools.glod_tools import GlodTools

tools = GlodTools()

# Access project information
overview = tools.get_project_overview()
config = tools.get_project_config()
available = tools.list_available_tools()
info = tools.get_full_project_info()

# Work with project files
content = tools.get_file_from_project("src/main.py")

# Save analysis results
tools.save_project_metadata(
    {"analysis": "results"},
    "agent_findings.json"
)
```

## Integration Points

### 1. In Agent Server

```python
# src/agents/agent_server.py
from src.server.tools.glod_tools import GlodTools

glod_tools = GlodTools()

# Add to agent's available tools
# Expose methods to agent for context-aware operations
```

### 2. In Client

```python
# src/client_agent.py
# Can request project metadata before sending prompts
project_info = agent.get_project_info()
```

### 3. In Custom Tools

```python
# .glod/tools/custom_analysis.py
from src.server.glod_api import GlodAPI

api = GlodAPI()
overview = api.get_overview()
# Use in custom analysis
```

## Workflow

### For Project Setup

1. **Create .glod**:
   ```bash
   python setup_glod.py
   ```

2. **Add overview.md**:
   - Edit `.glod/overview.md` with project information
   - Include architecture, structure, tech stack

3. **Add config.json** (optional):
   - Add machine-readable configuration
   - Define project conventions

4. **Add custom tools** (optional):
   - Create `.glod/tools/` directory
   - Add Python tools for specialized analysis

### For Agent Operation

1. **Load Context**:
   - Agent reads `.glod/overview.md`
   - Agent loads configuration
   - Agent discovers custom tools

2. **Use Context**:
   - Agent makes decisions based on project context
   - Agent follows project conventions
   - Agent uses custom tools

3. **Save Results**:
   - Agent saves analysis to `.glod/metadata/`
   - Results available for future runs

## Best Practices

### overview.md

- ✅ Clear project description
- ✅ Architecture overview
- ✅ Directory structure explained
- ✅ Key files and their purposes
- ✅ How to run/test the project
- ❌ Don't duplicate README (reference it instead)
- ❌ Don't include too much detail (keep it concise)

### config.json

- ✅ Machine-readable format
- ✅ Well-documented with comments
- ✅ Project type clearly specified
- ✅ Custom agent instructions
- ❌ Don't duplicate settings files
- ❌ Don't include secrets (use environment)

### Custom Tools

- ✅ Clear docstrings
- ✅ Type hints
- ✅ Focused purpose
- ✅ Well-tested
- ❌ Don't duplicate standard tools
- ❌ Don't make them too complex

## Examples

### Example 1: Python Project

```
.glod/
├── overview.md          # Python web app architecture
├── config.json          # Django/Flask settings reference
└── tools/
    └── django_analyzer.py  # Custom Django tools
```

### Example 2: Full-Stack Project

```
.glod/
├── overview.md          # Frontend + backend + database
├── config.json          # Full configuration
└── tools/
    ├── api_analyzer.py     # Analyze API
    ├── db_schema_analyzer.py  # Check database
    └── frontend_tester.py   # Frontend-specific tools
```

### Example 3: Minimal Project

```
.glod/
└── overview.md          # Just the overview
```

## Extending .glod

### Add New Metadata

1. Edit `.glod/overview.md` for human-readable info
2. Update `.glod/config.json` for configuration
3. Use `api.save_metadata()` to save analysis results

### Add Custom Tools

1. Create `.glod/tools/my_tool.py`
2. Implement functions with clear docstrings
3. Tools auto-discovered by `list_custom_tools()`

### Add Generated Metadata

```python
from src.server.glod_api import GlodAPI

api = GlodAPI()
api.save_metadata(
    {
        "analysis_date": "2024-01-15",
        "issues_found": 5,
        "code_coverage": 0.85,
        "recommendations": [...]
    },
    "analysis.json"
)
```

## Advantages

### For Agents
- ✅ Understand projects quickly
- ✅ Follow project conventions
- ✅ Make context-aware decisions
- ✅ Use project-specific tools
- ✅ Save and retrieve findings

### For Projects
- ✅ Standardized metadata format
- ✅ Version-controlled
- ✅ Portable across tools
- ✅ Easy to update
- ✅ No agent-specific code

### For Developers
- ✅ Document projects once
- ✅ Metadata for any tool
- ✅ Clear project structure
- ✅ Agent understands context
- ✅ Results saved for reference

## Troubleshooting

**Agent can't find .glod**
- Ensure `.glod/` is in project root
- Check path with `GlodAPI()._find_project_root()`

**Config.json not loading**
- Verify JSON syntax
- Check file encoding (UTF-8)
- Ensure it's in `.glod/config.json`

**Custom tools not discovered**
- Place `.py` files directly in `.glod/tools/`
- Include `__init__.py` in `tools/`
- Use clear docstrings

**Can't save metadata**
- Ensure `.glod/` directory exists
- Check write permissions
- Use absolute paths with `save_metadata()`

## Future Enhancements

- [ ] JSON Schema validation for config.json
- [ ] Tool dependency specification
- [ ] Integration with IDE metadata
- [ ] Project templates
- [ ] Metadata version history
- [ ] Multi-language support
- [ ] Integration with version control
- [ ] Cloud storage for shared metadata

