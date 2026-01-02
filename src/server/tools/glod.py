"""
GLOD Tools for Agent

This module provides tools for the coding agent to interact with project
metadata stored in the .glod folder. These tools allow the agent to:

- Understand project structure and purpose
- Access project-specific configuration
- List and use custom tools defined in .glod/tools/
- Query and save project metadata for context-aware responses
"""

from typing import Optional, Dict, Any, List
from pathlib import Path
from pydantic_ai import Tool

import server.lib.glod as glod_lib
from server.tools.util import _check_access


def get_project_overview(root: str) -> str:
    """
    Get a brief overview of the project.
    
    Retrieves the project's overview.md file from .glod/, providing context
    about what the project does, its architecture, and key information.
    
    Args:
        root: Path to project root
    
    Returns:
        Project overview text, or error message if not available
    """
    if not _check_access(root):
        return "error: access denied to this path"

    try:
        project_root = Path(root)
        overview = glod_lib.get_overview(project_root)
        
        if overview is None:
            return "Error: No project overview found. Create .glod/overview.md for better context."
        
        return overview
    except Exception as e:
        return f"error: {str(e)}"


def get_project_config(root: str) -> Dict[str, Any]:
    """
    Get project configuration from .glod/config.json.
    
    Retrieves machine-readable project configuration, which may include
    build settings, tool configurations, or project-specific metadata.
    
    Args:
        root: Path to project root
    
    Returns:
        Configuration dictionary, or empty dict if not found
    """
    if not _check_access(root):
        return {"error": "access denied to this path"}

    try:
        project_root = Path(root)
        config = glod_lib.get_config(project_root)
        
        if config is None:
            return {
                "status": "no_config",
                "message": "No config.json found in .glod/. Create one for custom configuration."
            }
        
        return config
    except Exception as e:
        return {"error": str(e)}


def list_available_tools(root: str) -> Dict[str, Any]:
    """
    List all custom tools available in .glod/tools/.
    
    Discovers custom toolsets defined in the project's .glod/tools/
    directory, which can provide project-specific functionality to the agent.
    
    Args:
        root: Path to project root
    
    Returns:
        Dictionary with list of tool names and their descriptions
    """
    if not _check_access(root):
        return {"error": "access denied to this path"}

    try:
        project_root = Path(root)
        tools = glod_lib.list_custom_tools(project_root)
        
        tool_info = {}
        for tool in tools:
            desc = glod_lib.get_custom_tool_info(project_root, tool)
            tool_info[tool] = desc or "No description available"
        
        return {
            "available_tools": tools,
            "count": len(tools),
            "details": tool_info
        }
    except Exception as e:
        return {"error": str(e)}


def get_full_project_info(root: str) -> Dict[str, Any]:
    """
    Get complete project information from .glod metadata.
    
    Provides a comprehensive view of all available project metadata in one call,
    useful for initial project understanding.
    
    Args:
        root: Path to project root
    
    Returns:
        Complete project information dictionary
    """
    if not _check_access(root):
        return {"error": "access denied to this path"}

    try:
        project_root = Path(root)
        return glod_lib.get_project_info(project_root)
    except Exception as e:
        return {"error": str(e)}


def get_file_from_project(root: str, relative_path: str) -> str:
    """
    Get the content of a file relative to project root.
    
    Reads files from the project while respecting the project root boundary,
    useful for understanding key project files.
    
    Args:
        root: Path to project root
        relative_path: Path relative to project root (e.g., 'src/main.py')
    
    Returns:
        File content, or error message if not found
    """
    if not _check_access(root):
        return "error: access denied to this path"

    try:
        project_root = Path(root)
        content = glod_lib.get_file_content(project_root, relative_path)
        
        if content is None:
            return f"error: file not found: {relative_path}"
        
        return content
    except Exception as e:
        return f"error: {str(e)}"


def save_project_metadata(root: str, metadata: Dict[str, Any], filename: str = "analysis.json") -> str:
    """
    Save analysis or metadata back to the .glod directory.
    
    Allows the agent to persist analysis results, findings, or other metadata
    to the project's .glod/ folder for future reference.
    
    Args:
        root: Path to project root
        metadata: Dictionary to save
        filename: Name of the JSON file to create in .glod/
    
    Returns:
        Success or error message
    """
    if not _check_access(root):
        return "error: access denied to this path"

    try:
        project_root = Path(root)
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        success = glod_lib.save_metadata(project_root, metadata, filename)
        
        if success:
            return f"success: metadata saved to .glod/{filename}"
        else:
            return f"error: failed to save metadata to .glod/{filename}"
    except Exception as e:
        return f"error: {str(e)}"


def get_project_structure_info(root: str) -> Dict[str, Any]:
    """
    Get information about the project structure from .glod metadata.
    
    Extracts structural information from the project overview, useful for
    understanding directories and key files.
    
    Args:
        root: Path to project root
    
    Returns:
        Dictionary with project structure information
    """
    if not _check_access(root):
        return {"error": "access denied to this path"}

    try:
        project_root = Path(root)
        overview = glod_lib.get_overview(project_root)
        
        if not overview:
            return {"status": "no_overview"}
        
        # Extract structure information
        structure_info = {
            "has_overview": True,
            "overview_length": len(overview),
            "is_large_project": len(overview) > 2000,
        }
        
        # Look for common directory patterns in overview
        if "src/" in overview:
            structure_info["has_src_dir"] = True
        if "tests/" in overview or "test/" in overview:
            structure_info["has_tests_dir"] = True
        if "docs/" in overview:
            structure_info["has_docs_dir"] = True
        
        return structure_info
    except Exception as e:
        return {"error": str(e)}


def get_pydantic_tools() -> List[Tool]:
    """
    Get all GLOD tools as Pydantic AI Tool objects.
    
    Returns:
        List of Tool objects for use with Pydantic AI agent
    """
    return [
        Tool(get_project_overview, takes_ctx=False),
        Tool(get_project_config, takes_ctx=False),
        Tool(list_available_tools, takes_ctx=False),
        Tool(get_full_project_info, takes_ctx=False),
        Tool(get_file_from_project, takes_ctx=False),
        Tool(save_project_metadata, takes_ctx=False),
        Tool(get_project_structure_info, takes_ctx=False),
    ]

