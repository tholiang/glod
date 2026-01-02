"""
Subagent spawning tools.

Allows the editor agent to spawn autonomous subagents with specific prompts and tools.
"""
from typing import List

from pydantic_ai import Agent, Tool
from pydantic_ai.models.anthropic import AnthropicModel


async def spawn_subagent(
    prompt: str,
    tool_names: List[str],
    context: str = ""
) -> str:
    """
    Spawn a subagent with a given prompt and set of tools.
    
    The subagent runs autonomously and independently from the parent agent.
    This is useful for delegating specialized tasks.
    
    Args:
        prompt: The task/question for the subagent to work on
        tool_names: List of tool names the subagent can use.
                   Valid names: 'list_files', 'read', 'grep', 'touch', 'delete', 
                   'rm', 'insert', 'replace', 'mkdir', 'mv' (file tools)
                   'git_status', 'git_add', 'git_commit', 'git_push', 'git_pull',
                   'git_log', 'git_diff', 'git_branch', 'git_checkout' (git tools)
        context: Optional context about the project or current state
    
    Returns:
        The subagent's response as a string
    """
    # Import here to avoid circular imports
    from server.tools import files, git
    
    # Map tool names to actual tool functions
    _tool_registry = {
        'list_files': files.list_files,
        'read': files.read,
        'grep': files.grep,
        'touch': files.touch,
        'delete': files.delete,
        'rm': files.rm,
        'insert': files.insert,
        'replace': files.replace,
        'mkdir': files.mkdir,
        'mv': files.mv,
        'git_status': git.git_status,
        'git_add': git.git_add,
        'git_commit': git.git_commit,
        'git_push': git.git_push,
        'git_pull': git.git_pull,
        'git_log': git.git_log,
        'git_diff': git.git_diff,
        'git_branch': git.git_branch,
        'git_checkout': git.git_checkout,
    }
    
    # Validate and get requested tools
    invalid_tools = [name for name in tool_names if name not in _tool_registry]
    if invalid_tools:
        return f"error: invalid tool names: {invalid_tools}"
    
    selected_tools = [Tool(_tool_registry[name], takes_ctx=False) for name in tool_names]
    
    # Build system prompt for subagent
    sys_prompt = f"""You are a specialized autonomous subagent.

Your task: {prompt}

{f'Context: {context}' if context else ''}

Use the available tools to complete your task. Be direct and efficient.
Report your findings and actions clearly."""
    
    # Run the subagent
    model = AnthropicModel('claude-haiku-4-5')
    agent = Agent(
        model,
        system_prompt=sys_prompt,
        tools=selected_tools if selected_tools else []
    )
    
    try:
        result = await agent.run(prompt)
        return result.output
    except Exception as e:
        return f"error: subagent failed: {e}"


def get_pydantic_agent_tools() -> List[Tool]:
    """Get agent spawning tools as pydantic-ai Tool objects"""
    return [
        Tool(spawn_subagent, takes_ctx=False),
    ]
