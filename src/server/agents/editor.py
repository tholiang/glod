import os
from typing import List, AsyncGenerator

from pydantic_ai import Agent, AgentRunResultEvent, FunctionToolCallEvent, FunctionToolResultEvent, PartDeltaEvent, PartEndEvent, PartStartEvent, RetryPromptPart, TextPart, TextPartDelta, ToolCallPart, BuiltinToolCallPart, BuiltinToolReturnPart, ThinkingPart, FilePart, ToolReturnPart, ModelMessage
from pydantic_ai.models.anthropic import AnthropicModel

from server.tools import files
from server.app import get_app

_DEFAULT_SYS_PROMPT = f"""
You are a basic coding assistant. Use the provided tools to edit files based on user instruction
"""

def _sys_prompt_with_dirs() -> str:
    app = get_app()
    dirs = [str(path) for path in app.get_allowed_paths()]

    return f"""
{_DEFAULT_SYS_PROMPT}
allowed directories:{'\n'.join(dirs)}
"""
    
async def editor_run(prompt: str, message_history: List[ModelMessage]) -> str:
    """Run agent with provided message history (stateless)"""
    model = AnthropicModel('claude-haiku-4-5')
    agent = Agent(
        model,
        system_prompt=_sys_prompt_with_dirs(),
        tools=files.get_pydantic_tools()
    )
    result = await agent.run(prompt, message_history=message_history)
    message_history.extend(result.new_messages())
    return result.output

async def editor_run_stream(prompt: str, message_history: List[ModelMessage]) -> AsyncGenerator[str]:
    """
    Streaming version that yields events as they occur.
    
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
        tools=files.get_pydantic_tools()
    )
    
    async for event in agent.run_stream_events(prompt, message_history=message_history):
        if isinstance(event, PartStartEvent):
            if isinstance(event.part, TextPart):
                yield event.part.content
        elif isinstance(event, PartDeltaEvent):
            if isinstance(event.delta, TextPartDelta):
                yield event.delta.content_delta
        elif isinstance(event, FunctionToolCallEvent):
            yield f"\n----------\ncalling tool: {event.part.tool_name} {event.part.args}\n...\n"
        elif isinstance(event, FunctionToolResultEvent):
            if isinstance(event.result, ToolReturnPart):
                output = str(event.result.content)
                if len(output.splitlines()) > 10:
                    yield "10 line output\n----------\n"
                else:
                    yield f"\ncalling tool: {event.result.content}\n----------\n"
            elif isinstance(event.result, RetryPromptPart):
                yield f"\nretry: {event.result.content}"
        elif isinstance(event, AgentRunResultEvent):
            message_history.extend(event.result.new_messages())


