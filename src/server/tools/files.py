from typing import List
import os
from pathlib import Path
import subprocess
import shutil
from datetime import datetime
from pydantic_ai import Tool

from server.tools.util import _check_access

def list_files(filepath: str, recursive: bool = False) -> List[str]:
    """
    Lists files under a directory. Optionally recursively include files.
    
    Returns:
        - Non-recursive: List of filenames in the directory
        - Recursive: List of full paths to all files (limited to 100 files)
    """
    if not _check_access(filepath):
        return ["error: access denied to this path"]
    
    try:
        if not recursive:
            items = os.listdir(filepath)
            # Return full paths for consistency
            return [os.path.join(filepath, item) for item in items if os.path.isfile(os.path.join(filepath, item))]
        
        ret = []
        for root, dirs, files in os.walk(filepath):
            for file in files:
                full_path = os.path.join(root, file)
                ret.append(full_path)
        
        if len(ret) > 100:
            return [f"error: too many files found: {len(ret)}. Use non-recursive mode or filter your search."]
        return ret
    except Exception as e:
        return [f"error: {e}"]

def read(filepath: str, start_line: int = 1, end_line: int = 1000) -> str:
    """
    Read a file
    
    Args:
        filepath: Path to the file to read
        start_line: first line to read (1-indexed, default 1)
        end_line: last line to read (1-indexed, default 1000)
    
    Returns:
        File contents prefixed with line numbers ("1: "), or error message if file is too large
    """
    if not _check_access(filepath):
        return "error: access denied to this path"
    
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()
            ret = []
            for i in range(start_line-1, min(end_line-1, len(lines))):
                ret.append(f"{i}: {lines[i]}")
            return '\n'.join(ret)
    except Exception as e:
        return f"error: {e}"

def grep(filepath: str, pattern: str, flags: List[str] = []) -> str:
    """
    Search a file for a given pattern using grep.
    
    Args:
        filepath: Path to the file to search
        pattern: Pattern to search for
        flags: Optional grep flags (e.g., ['-n'] for line numbers, ['-i'] for case-insensitive)
               Recommend using ['-n'] to include line numbers in results
    
    Returns:
        Matching lines from the file, or error message
    """
    if not _check_access(filepath):
        return "error: access denied to this path"
    
    try:
        # Correct order: grep [flags] pattern filepath
        cmd = ['grep'] + flags + [pattern, filepath]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            return result.stdout
        elif result.returncode == 1:
            return "error: no matches found"
        else:
            return f"error: grep failed with code {result.returncode}: {result.stderr}"
    except Exception as e:
        return f"error: {e}"
    
def mkdir(filepath: str) -> str:
    """
    Create a new empty directory
    
    Returns:
        Success message, or error message
    """
    if not _check_access(filepath):
        return "error: access denied to this path"
    
    try:
        subprocess.run(['mkdir', filepath], check=True)
        return f"success: directory created: {filepath}"
    except Exception as e:
        return f"error: {e}"

def touch(filepath: str) -> str:
    """
    Create a new empty file, or update the timestamp of an existing file.
    
    Returns:
        Success message, or error message
    """
    if not _check_access(filepath):
        return "error: access denied to this path"
    
    try:
        subprocess.run(['touch', filepath], check=True)
        return f"success: file created or updated: {filepath}"
    except Exception as e:
        return f"error: {e}"

def mv(source: str, dest: str) -> str:
    """
    Move a file to a new location
    
    Returns:
        Success message, or error message
    """
    if not _check_access(source):
        return f"error: access denied to this path {source}"
    if not _check_access(dest):
        return f"error: access denied to this path {dest}"
    
    try:
        subprocess.run(['mv', source, dest], check=True)
        return f"success: file {source} moved to {dest}"
    except Exception as e:
        return f"error: {e}"

def delete(filepath: str, start_line: int, end_line: int) -> str:
    """
    Delete lines from a file (inclusive, 1-indexed).
    
    Args:
        filepath: Path to the file
        start_line: Starting line number (1-indexed, inclusive)
        end_line: Ending line number (1-indexed, inclusive)
    
    Returns:
        Success message with backup location, or error message
    
    Example:
        delete('file.py', 5, 10) deletes lines 5, 6, 7, 8, 9, 10
    """
    if not _check_access(filepath):
        return "error: access denied to this path"
    
    if start_line < 1 or end_line < 1 or start_line > end_line:
        return "error: invalid line numbers. start_line and end_line must be >= 1 and start_line <= end_line"
    
    try:
        
        with open(filepath, 'r') as file:
            content = file.readlines()
        
        # Convert from 1-indexed to 0-indexed for Python slicing
        # end_line + 1 because slice is exclusive on the right
        del content[start_line - 1:end_line]

        with open(filepath, 'w') as file:
            file.write(''.join(content))
        
        return f"success: deleted lines {start_line}-{end_line}"
    except Exception as e:
        return f"error: {e}"
        
def rm(filepath: str, recursive: bool = False) -> str:
    """
    Delete a file or directory.
    
    Args:
        filepath: Path to the file or directory to delete
        recursive: If True, recursively delete directories and their contents
    
    Returns:
        Success message, or error message
    
    Example:
        rm('/path/to/file.txt') deletes a file
        rm('/path/to/directory', recursive=True) deletes directory and contents
    """
    if not _check_access(filepath):
        return "error: access denied to this path"
    
    try:
        path = Path(filepath)
        
        if not path.exists():
            return f"error: path does not exist: {filepath}"
        
        if path.is_file():
            path.unlink()
            return f"success: deleted file: {filepath}"
        elif path.is_dir():
            if recursive:
                shutil.rmtree(path)
                return f"success: deleted directory recursively: {filepath}"
            else:
                return f"error: {filepath} is a directory. Use recursive=True to delete directories."
        else:
            return f"error: {filepath} is not a file or directory"
    except Exception as e:
        return f"error: {e}"

def insert(filepath: str, line_number: int, text: str) -> str:
    """
    Insert lines into a file at the specified position (1-indexed).
    
    Args:
        filepath: Path to the file
        line_number: Line number where to insert (1-indexed, inserts BEFORE this line)
        text: Text to insert (newlines will be added automatically)
    
    Returns:
        Success message with backup location, or error message
    
    Example:
        insert('file.py', 5, 'new code') inserts 'new code' before line 5
    """
    if not _check_access(filepath):
        return "error: access denied to this path"
    
    if line_number < 1:
        return "error: line_number must be >= 1"
    
    try:
        with open(filepath, 'r') as file:
            content = file.readlines()
        
        # Convert from 1-indexed to 0-indexed for Python list.insert()
        content.insert(line_number - 1, text + '\n')
        
        with open(filepath, 'w') as file:
            file.write(''.join(content))
        
        return f"success: inserted text at line {line_number}"
    except Exception as e:
        return f"error: {e}"


def replace(filepath: str, start_line: int, end_line: int, text: str) -> str:
    """
    Replace lines in a file (1-indexed) with provided text.
    
    Args:
        filepath: Path to the file
        start_line: Line number where start replacement (inclusive)
        end_line: Line number where end replacement (inclusive)
        text: Text to insert (newlines will be added automatically)
    
    Returns:
        Success message or error message
    """
    delete_resp = delete(filepath, start_line, end_line)
    if "error" in delete_resp:
        return delete_resp
    insert_resp = insert(filepath, start_line, text)
    if "error" in insert_resp:
        return insert_resp
    return f"success: replaced text from {start_line}:{end_line}"


def get_pydantic_tools() -> List[Tool]:
    return [
        Tool(list_files, takes_ctx=False, max_retries=3),
        Tool(read, takes_ctx=False, max_retries=3),
        Tool(grep, takes_ctx=False, max_retries=3),
        Tool(touch, takes_ctx=False, max_retries=3),
        Tool(delete, takes_ctx=False, max_retries=3),
        Tool(rm, takes_ctx=False, max_retries=3),
        Tool(insert, takes_ctx=False, max_retries=3),
        Tool(replace, takes_ctx=False, max_retries=3),
        Tool(mkdir, takes_ctx=False, max_retries=3),
        Tool(mv, takes_ctx=False, max_retries=3)
    ]
