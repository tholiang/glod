"""
Tool call validation and error recovery.

Validates tool parameters before execution to catch issues early,
and provides recovery strategies for common errors.
"""
import json
from typing import Any, Optional


class ToolValidator:
    """Validate tool calls before they're executed."""
    
    MAX_PARAM_SIZE = 100 * 1024  # 100KB per parameter
    MAX_TOTAL_SIZE = 500 * 1024  # 500KB total
    
    @staticmethod
    def validate_insert_tool(filepath: str, line_number: int, text: str) -> tuple[bool, Optional[str]]:
        """
        Validate insert tool parameters.
        
        Returns:
            (is_valid, error_message_or_none)
        """
        if not isinstance(filepath, str) or not filepath:
            return False, "filepath must be a non-empty string"
        
        if not isinstance(line_number, int) or line_number < 1:
            return False, "line_number must be a positive integer"
        
        if not isinstance(text, str):
            return False, "text must be a string"
        
        text_size = len(text.encode('utf-8'))
        if text_size > ToolValidator.MAX_PARAM_SIZE:
            return False, (
                f"text too large: {text_size} bytes (max {ToolValidator.MAX_PARAM_SIZE}). "
                f"Use chunking instead."
            )
        
        return True, None
    
    @staticmethod
    def validate_read_tool(filepath: str, max_lines: Optional[int] = None) -> tuple[bool, Optional[str]]:
        """Validate read tool parameters."""
        if not isinstance(filepath, str) or not filepath:
            return False, "filepath must be a non-empty string"
        
        if max_lines is not None and (not isinstance(max_lines, int) or max_lines < 1):
            return False, "max_lines must be a positive integer"
        
        return True, None
    
    @staticmethod
    def validate_delete_tool(filepath: str, start_line: int, end_line: int) -> tuple[bool, Optional[str]]:
        """Validate delete tool parameters."""
        if not isinstance(filepath, str) or not filepath:
            return False, "filepath must be a non-empty string"
        
        if not isinstance(start_line, int) or start_line < 1:
            return False, "start_line must be a positive integer"
        
        if not isinstance(end_line, int) or end_line < start_line:
            return False, "end_line must be >= start_line"
        
        return True, None
    
    @staticmethod
    def validate_tool_call_json(tool_name: str, params: dict) -> tuple[bool, Optional[str]]:
        """
        Validate that a complete tool call can be serialized.
        
        This catches JSON truncation issues early.
        """
        try:
            tool_call = {
                "type": "tool_use",
                "id": f"tool_{tool_name}",
                "name": tool_name,
                "input": params
            }
            
            serialized = json.dumps(tool_call)
            size = len(serialized.encode('utf-8'))
            
            if size > ToolValidator.MAX_TOTAL_SIZE:
                return False, (
                    f"Tool call too large: {size} bytes (max {ToolValidator.MAX_TOTAL_SIZE}). "
                    f"Parameters are too big to serialize."
                )
            
            return True, None
        
        except Exception as e:
            return False, f"Failed to serialize tool call: {str(e)}"


class ErrorRecovery:
    """Strategies for recovering from common tool call errors."""
    
    @staticmethod
    def handle_json_invalid() -> str:
        """Recovery suggestion for invalid JSON."""
        return (
            "JSON parsing failed. This usually means:\n"
            "1. Tool parameter 'text' is too large - consider splitting it\n"
            "2. Special characters in text need escaping\n"
            "3. Newlines in text need proper formatting\n\n"
            "Try:\n"
            "- Use chunking for large insertions (>2KB)\n"
            "- Check for unescaped quotes or backslashes\n"
            "- Use \\n for newlines instead of literal newlines"
        )
    
    @staticmethod
    def handle_truncated_json() -> str:
        """Recovery suggestion for truncated JSON."""
        return (
            "JSON was truncated during serialization. Usually means:\n"
            "1. Text parameter is too large\n"
            "2. Response buffer overflowed\n\n"
            "Solutions:\n"
            "- Split large insertions into chunks (max 2KB each)\n"
            "- Read file structure first to understand what to change\n"
            "- Make smaller, more focused changes"
        )
    
    @staticmethod
    def suggest_chunking_strategy(text_size: int) -> str:
        """Suggest how to chunk a large insertion."""
        chunk_size = 2000
        num_chunks = (text_size // chunk_size) + 1
        
        return (
            f"Text is {text_size} bytes. Recommended chunking:\n"
            f"- Split into ~{num_chunks} chunks of {chunk_size} bytes each\n"
            f"- Insert each chunk sequentially\n"
            f"- Or use get_file_structure() to understand file first, "
            f"then make smaller targeted changes"
        )

