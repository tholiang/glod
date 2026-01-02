import os
from typing import List, AsyncGenerator

from pydantic_ai import Agent, AgentRunResultEvent, FunctionToolCallEvent, FunctionToolResultEvent, PartDeltaEvent, PartEndEvent, PartStartEvent, RetryPromptPart, TextPart, TextPartDelta, ToolCallPart, BuiltinToolCallPart, BuiltinToolReturnPart, ThinkingPart, FilePart, ToolReturnPart, ModelMessage
from pydantic_ai.models.anthropic import AnthropicModel
from server.app import get_app
from server.tools import files, git, agents

_DEFAULT_SYS_PROMPT = f"""
You are a coding assistant helping develop GLOD.

Use the provided tools to edit files based on user instruction.

DOCUMENTATION: 
- Read .glod/ to understand the project
- Keep .glod/ updated as you work:
- Update .glod/overview.md when architecture/components change
- Create .glod/[feature].md for new major features (concise, technical, agent-facing)
- Delete .glod/[feature].md when features are removed
- Keep all docs concise - no lengthy explanations or checklists
- Only document what's needed for future work on this codebase

Be minimal with documentation. Only create what explains how something works.
Do not make checklists or progress reports. Keep doc files to a single file per component.
Use the `get_project_overview` tool to gain context about the project.

You also have access to git tools for version control operations.
You can spawn subagents for specialized tasks using the spawn_subagent tool.
"""

def _sys_prompt_with_dirs() -> str:
    app = get_app()
    dirs = [str(path) for path in app.get_allowed_paths()]

    return f"""
{_DEFAULT_SYS_PROMPT}
allowed directories:{'\n'.join(dirs)}
"""

def _get_all_tools() -> List:
    """Get all available tools: file operations, git operations, and subagent spawning"""
    return files.get_pydantic_tools() + git.get_pydantic_git_tools() + agents.get_pydantic_agent_tools()
    
async def editor_run(prompt: str, message_history: List[ModelMessage]) -> str:
    """Run agent with provided message history (stateless)"""
    model = AnthropicModel('claude-haiku-4-5')
    agent = Agent(
        model,
        system_prompt=_sys_prompt_with_dirs(),
        tools=_get_all_tools()
    )
    result = await agent.run(prompt, message_history=message_history)
    message_history.extend(result.new_messages())
    return result.output

async def editor_run_stream(prompt: str, message_history: List[ModelMessage]) -> AsyncGenerator[tuple[str, str]]:
    """
    Streaming version that yields (event_type, content) tuples.
    
    Event types:
    - "chunk": Regular response text
    - "tool_call": Tool invocation with name and args
    - "tool_result": Result from tool execution
    
    After streaming is complete, call get_new_messages() to get messages
    to add to client history.
    
    The message_history is passed in (stateless), so you can:
    - Restart the agent without affecting client conversation history
    - Switch agents while maintaining client session
    - Persist history independently on client side
    """
    model = AnthropicModel('claude-haiku-4-5')
    agent = Agent(
        model,
        system_prompt=_sys_prompt_with_dirs(),
        tools=_get_all_tools()
    )
    
    async for event in agent.run_stream_events(prompt, message_history=message_history):
        if isinstance(event, PartStartEvent):
            if isinstance(event.part, TextPart):
                yield ("chunk", event.part.content)
        elif isinstance(event, PartDeltaEvent):
            if isinstance(event.delta, TextPartDelta):
                yield ("chunk", event.delta.content_delta)
        elif isinstance(event, FunctionToolCallEvent):
            # Emit tool call event with clean formatting
            tool_call_str = f"{event.part.tool_name}({event.part.args})"
            yield ("tool_call", tool_call_str)
        elif isinstance(event, FunctionToolResultEvent):
            if isinstance(event.result, ToolReturnPart):
                output = str(event.result.content)
                # Emit tool result event
                yield ("tool_result", output)
            elif isinstance(event.result, RetryPromptPart):
                yield ("tool_result", f"retry: {event.result.content}")
        elif isinstance(event, AgentRunResultEvent):
            message_history.extend(event.result.new_messages())

