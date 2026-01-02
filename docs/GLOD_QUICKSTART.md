# .glod Quick Start Guide

Get your project set up with `.glod` metadata in 5 minutes!

## What is .glod?

`.glod` is a folder that stores project metadata helping the AI coding agent understand your project. It's generic, portable, and works with any project.

## Quick Start

### Step 1: Initialize .glod

In your project root:

```bash
python setup_glod.py
```

This creates:
```
.glod/
├── overview.md
└── tools/
    └── __init__.py
```

### Step 2: Edit overview.md

Edit `.glod/overview.md` with your project information:

```markdown
# My Project Name

## What does this project do?
Brief description of your project.

## Architecture
How is your project structured?

## Technology Stack
- Language: Python 3.11
- Framework: FastAPI
- Database: PostgreSQL

## Project Structure
```
src/
├── main.py        # Entry point
├── models/        # Data models
└── routes/        # API routes
```

## Key Files
| File | Purpose |
|------|---------|
| `src/main.py` | Application entry point |
| `src/config.py` | Configuration |

## How to Run
```bash
pip install -r requirements.txt
python src/main.py
```
```

### Step 3 (Optional): Add config.json

For machine-readable configuration:

```bash
cat > .glod/config.json << 'EOF'
{
  "project_name": "My Project",
  "language": "python",
  "framework": "fastapi",
  "main_entry": "src/main.py",
  "directories": {
    "src": "Source code",
    "tests": "Test files",
    "docs": "Documentation"
  }
}
EOF
```

### Step 4: Use in Agent

The agent can now access your metadata:

```python
from src.server.tools.glod_tools import GlodTools

tools = GlodTools()

# Get project overview
overview = tools.get_project_overview()

# Get configuration
config = tools.get_project_config()

# Get project info
info = tools.get_full_project_info()
```

## Common Tasks

### Add Custom Tools

Create `.glod/tools/my_analyzer.py`:

```python
"""
Custom analysis tools for this project.

Provides specialized analysis specific to our architecture.
"""

def analyze_code_style():
    """Check code style compliance."""
    return {"style_issues": [...]}

def find_test_coverage():
    """Calculate test coverage."""
    return {"coverage": 0.85}
```

Agent automatically discovers it!

### Save Analysis Results

```python
tools.save_project_metadata(
    {
        "analysis_date": "2024-01-15",
        "issues": ["Issue 1", "Issue 2"],
        "recommendations": ["Fix 1", "Fix 2"]
    },
    "analysis.json"
)
```

Results saved to `.glod/analysis.json`

### Read Project Files

```python
# Read a file relative to project root
content = tools.get_file_from_project("src/main.py")
```

## Examples

### Python Project

```
.glod/
├── overview.md      # Python + FastAPI project
├── config.json      # FastAPI config reference
└── tools/
    └── code_analyzer.py  # Custom analysis
```

**overview.md includes**:
- FastAPI architecture
- Endpoint structure
- Authentication approach
- Database schema

### Web Project

```
.glod/
├── overview.md      # Frontend + backend
└── config.json      # Full stack config
```

**overview.md includes**:
- Frontend framework (React, Vue, etc.)
- Backend framework
- API endpoints
- Database schema
- Deployment setup

### Simple Project

Just a basic overview:

```
.glod/
└── overview.md
```

**overview.md includes**:
- What the project does
- How to run it
- Key files

## Best Practices

✅ **Do**:
- Keep overview.md concise but informative
- Update overview.md when project changes
- Use config.json for agent instructions
- Create custom tools for common analysis
- Commit .glod to version control

❌ **Don't**:
- Duplicate entire README
- Store secrets in config.json
- Create overly complex custom tools
- Leave placeholder text in overview.md

## Checklist

- [ ] Created `.glod/` directory
- [ ] Wrote `.glod/overview.md`
- [ ] Updated with project information
- [ ] (Optional) Created `.glod/config.json`
- [ ] (Optional) Added custom tools to `.glod/tools/`
- [ ] Committed to version control
- [ ] Verified agent can read metadata

## Verification

Test that everything works:

```python
from src.server.tools.glod_tools import GlodTools

tools = GlodTools()

# Should return your overview
overview = tools.get_project_overview()
assert overview is not None
assert "Project Name" in overview  # Check your content is there

# Should return tools list
available = tools.list_available_tools()
print(f"Available tools: {available}")

# Should return full info
info = tools.get_full_project_info()
assert info["glod_exists"] == True
```

## Troubleshooting

**Agent can't find .glod**
```python
from src.server.glod_api import GlodAPI
api = GlodAPI()
print(api.glod_dir)  # Check if path is correct
```

**override.md not loading**
- Check file encoding (use UTF-8)
- Verify it's in `.glod/` directory
- Check file permissions

**Custom tools not discovered**
```python
tools_list = api.list_custom_tools()
print(tools_list)  # Should include your tools
```

## Next Steps

1. ✅ Initialize .glod
2. ✅ Write overview.md
3. ✅ (Optional) Add config.json
4. ✅ (Optional) Add custom tools
5. 🚀 Use with agent!

## Learn More

- **[GLOD_INFRASTRUCTURE.md](GLOD_INFRASTRUCTURE.md)** - Complete .glod documentation
- **[.glod/overview.md](../.glod/overview.md)** - Example overview for this project

## Questions?

Check:
1. `.glod/overview.md` in this project for examples
2. `GLOD_INFRASTRUCTURE.md` for detailed docs
3. `src/server/glod_api.py` for API reference
4. `src/server/tools/glod_tools.py` for tool reference

