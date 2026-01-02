# Subagent Spawning

The editor agent can spawn autonomous subagents to handle specialized tasks.

## Implementation

- **Tool**: `spawn_subagent` in `src/server/tools/agents.py`
- **Function signature**:
  ```python
  async def spawn_subagent(
      prompt: str,
      tool_names: List[str],
      context: str = ""
  ) -> str
  ```

## Usage

The main agent calls `spawn_subagent` with:
- `prompt`: The task for the subagent
- `tool_names`: List of tool names (file or git operations)
- `context`: Optional project context

## Available Tools

**File operations**: `list_files`, `read`, `grep`, `touch`, `delete`, `rm`, `insert`, `replace`, `mkdir`, `mv`

**Git operations**: `git_status`, `git_add`, `git_commit`, `git_push`, `git_pull`, `git_log`, `git_diff`, `git_branch`, `git_checkout`

## Design

- Subagents run independently with custom system prompts
- Each gets an isolated set of tools (no recursive spawning)
- Uses Haiku model for cost efficiency
- Returns output as string
