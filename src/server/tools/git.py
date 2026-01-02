"""
Git tools for the agent using subprocess commands.

Provides basic git operations:
- git_status: Check repository status
- git_add: Stage files for commit
- git_commit: Create a commit
- git_push: Push changes to remote
- git_pull: Pull changes from remote
- git_log: View commit history
- git_diff: Show changes
- git_branch: List or create branches
- git_checkout: Switch branches
"""
from typing import List
import subprocess
from pathlib import Path

from pydantic_ai import Tool

from server.tools.util import _check_access


def git_status(repo_path: str = ".") -> str:
    """
    Check the status of a git repository.
    
    Args:
        repo_path: Path to the git repository (default: current directory)
    
    Returns:
        Git status output, or error message
    """
    if not _check_access(repo_path):
        return "error: access denied to this path"
    
    try:
        result = subprocess.run(
            ['git', 'status'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "error: git status command timed out"
    except Exception as e:
        return f"error: {e}"


def git_add(files: List[str], repo_path: str = ".") -> str:
    """
    Stage files for commit.
    
    Args:
        files: List of file paths to stage (e.g., ['file.py', 'src/'])
               Use ['.'] to stage all changes
        repo_path: Path to the git repository (default: current directory)
    
    Returns:
        Success message, or error message
    """
    if not _check_access(repo_path):
        return "error: access denied to this path"
    
    try:
        cmd = ['git', 'add'] + files
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return f"success: staged {len(files)} file(s)"
        else:
            return f"error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "error: git add command timed out"
    except Exception as e:
        return f"error: {e}"


def git_commit(message: str, repo_path: str = ".") -> str:
    """
    Create a commit with staged changes.
    
    Args:
        message: Commit message
        repo_path: Path to the git repository (default: current directory)
    
    Returns:
        Commit output or error message
    """
    if not _check_access(repo_path):
        return "error: access denied to this path"
    
    try:
        result = subprocess.run(
            ['git', 'commit', '-m', message],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "error: git commit command timed out"
    except Exception as e:
        return f"error: {e}"


def git_push(branch: str = "", repo_path: str = ".") -> str:
    """
    Push commits to remote repository.
    
    Args:
        branch: Branch name to push (empty string for current branch)
        repo_path: Path to the git repository (default: current directory)
    
    Returns:
        Push output or error message
    """
    if not _check_access(repo_path):
        return "error: access denied to this path"
    
    try:
        cmd = ['git', 'push']
        if branch:
            cmd.append(branch)
        
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "error: git push command timed out"
    except Exception as e:
        return f"error: {e}"


def git_pull(repo_path: str = ".") -> str:
    """
    Pull changes from remote repository.
    
    Args:
        repo_path: Path to the git repository (default: current directory)
    
    Returns:
        Pull output or error message
    """
    if not _check_access(repo_path):
        return "error: access denied to this path"
    
    try:
        result = subprocess.run(
            ['git', 'pull'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "error: git pull command timed out"
    except Exception as e:
        return f"error: {e}"


def git_log(num_commits: int = 10, repo_path: str = ".") -> str:
    """
    View commit history.
    
    Args:
        num_commits: Number of commits to show (default: 10)
        repo_path: Path to the git repository (default: current directory)
    
    Returns:
        Commit log or error message
    """
    if not _check_access(repo_path):
        return "error: access denied to this path"
    
    try:
        result = subprocess.run(
            ['git', 'log', f'-n {num_commits}', '--oneline'],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "error: git log command timed out"
    except Exception as e:
        return f"error: {e}"


def git_diff(file_path: str = "", repo_path: str = ".") -> str:
    """
    Show changes in the repository.
    
    Args:
        file_path: Optional specific file to show diff for (empty for all changes)
        repo_path: Path to the git repository (default: current directory)
    
    Returns:
        Diff output or error message
    """
    if not _check_access(repo_path):
        return "error: access denied to this path"
    
    try:
        cmd = ['git', 'diff']
        if file_path:
            cmd.append(file_path)
        
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return result.stdout if result.stdout else "no changes"
        else:
            return f"error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "error: git diff command timed out"
    except Exception as e:
        return f"error: {e}"


def git_branch(branch_name: str = "", repo_path: str = ".") -> str:
    """
    List branches or create a new branch.
    
    Args:
        branch_name: Name of branch to create (empty to list all branches)
        repo_path: Path to the git repository (default: current directory)
    
    Returns:
        Branch list or creation confirmation, or error message
    """
    if not _check_access(repo_path):
        return "error: access denied to this path"
    
    try:
        if branch_name:
            # Create new branch
            cmd = ['git', 'branch', branch_name]
        else:
            # List branches
            cmd = ['git', 'branch', '-a']
        
        result = subprocess.run(
            cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "error: git branch command timed out"
    except Exception as e:
        return f"error: {e}"


def git_checkout(branch: str, repo_path: str = ".") -> str:
    """
    Switch to a different branch.
    
    Args:
        branch: Branch name to checkout
        repo_path: Path to the git repository (default: current directory)
    
    Returns:
        Checkout confirmation or error message
    """
    if not _check_access(repo_path):
        return "error: access denied to this path"
    
    if not branch:
        return "error: branch name is required"
    
    try:
        result = subprocess.run(
            ['git', 'checkout', branch],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return "error: git checkout command timed out"
    except Exception as e:
        return f"error: {e}"


def get_pydantic_git_tools() -> List[Tool]:
    """Get all git tools as pydantic-ai Tool objects"""
    return [
        Tool(git_status, takes_ctx=False),
        Tool(git_add, takes_ctx=False),
        Tool(git_commit, takes_ctx=False),
        Tool(git_push, takes_ctx=False),
        Tool(git_pull, takes_ctx=False),
        Tool(git_log, takes_ctx=False),
        Tool(git_diff, takes_ctx=False),
        Tool(git_branch, takes_ctx=False),
        Tool(git_checkout, takes_ctx=False),
    ]

