# Git Tools

The agent has access to basic git tools for version control operations using subprocess commands.

## Available Tools

### git_status(repo_path=".")
Check the status of a git repository.

```python
git_status()  # Check current directory
git_status("/path/to/repo")  # Check specific repo
```

Returns the output of `git status`.

### git_add(files, repo_path=".")
Stage files for commit.

```python
git_add(["file.py", "src/"])  # Stage specific files
git_add(["."])  # Stage all changes
```

### git_commit(message, repo_path=".")
Create a commit with staged changes.

```python
git_commit("Fix bug in parser")
```

### git_push(branch="", repo_path=".")
Push commits to remote repository.

```python
git_push()  # Push current branch
git_push("main")  # Push specific branch
```

### git_pull(repo_path=".")
Pull changes from remote repository.

```python
git_pull()
```

### git_log(num_commits=10, repo_path=".")
View commit history.

```python
git_log()  # Show last 10 commits
git_log(20)  # Show last 20 commits
```

### git_diff(file_path="", repo_path=".")
Show changes in the repository.

```python
git_diff()  # Show all changes
git_diff("file.py")  # Show changes for specific file
```

### git_branch(branch_name="", repo_path=".")
List branches or create a new branch.

```python
git_branch()  # List all branches
git_branch("feature/new-feature")  # Create new branch
```

### git_checkout(branch, repo_path=".")
Switch to a different branch.

```python
git_checkout("main")
git_checkout("feature/new-feature")
```

## Implementation

All git tools use subprocess to execute git commands directly. They:

- Check access permissions via `_check_access()` before running
- Have a 10-30 second timeout to prevent hangs
- Return error messages on failure
- Support an optional `repo_path` parameter (defaults to current directory ".")

## Example Workflow

```
> Make a commit with the message "Update documentation"
[Agent stages changes and creates commit]

> Show me the last 5 commits
[Agent displays commit history]

> Switch to the development branch
[Agent checks out dev branch]
```

