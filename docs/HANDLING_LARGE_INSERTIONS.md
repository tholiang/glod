# Handling Large Code Insertions

## Problem

When the agent tries to insert large amounts of code (>2KB), JSON serialization can fail:

```
Invalid JSON: EOF while parsing an object at line 1 column 100
```

This happens because:
1. **JSON gets truncated** - Large parameter values cut off mid-serialization
2. **Token limits** - Very large code exceeds parameter size limits
3. **Escaping overhead** - Special characters increase encoded size
4. **Buffer overflows** - Response serialization buffer overflows

## Solutions

### Solution 1: Automatic Chunking (Best)

The `insert` tool now automatically chunks large insertions:

```python
# In agent or system:
from src.tools.file_tools import FileTool

# Works even with 100KB+ of code
result = FileTool.insert_text(
    filepath="/path/to/file.py",
    line_number=10,
    text=very_large_code  # Automatically chunks if >2KB
)

# Returns: {"status": "success", "chunks": 5}
```

**How it works:**
1. Detects if text > 2KB
2. Splits into 2KB chunks
3. Inserts chunks sequentially 
4. Preserves line structure

### Solution 2: Manual Chunking (For Control)

Use the chunking utility directly:

```python
from src.tools.chunking import split_large_insertion

# Split code into chunks
chunks = split_large_insertion(large_code, chunk_size=2000)

# Insert each chunk
from src.tools.file_tools import FileTool
for i, chunk in enumerate(chunks):
    FileTool.insert_text(
        filepath="file.py",
        line_number=10 + i,  # Increment for each chunk
        text=chunk['text']
    )
```

### Solution 3: Understand File Structure First (Recommended)

Instead of inserting lots of code, understand the file structure and make targeted changes:

```python
from src.tools.file_tools import FileTool

# Get file structure without reading everything
structure = FileTool.get_file_structure("src/main.py")
# Returns: classes, functions, imports, line numbers

# Now you know exactly where to insert
# Make smaller, focused changes instead
```

### Solution 4: Size Validation Before Sending

Check parameter size before calling tool:

```python
from src.tools.chunking import validate_json_serializable, estimate_json_size

# Check before insertion
size = estimate_json_size(code_to_insert)
if size > 50000:  # 50KB
    print("Text too large, use chunking")
    chunks = split_large_insertion(code_to_insert)
```

## Best Practices

### ✅ DO:

1. **Use file structure analysis first**
   ```python
   # Before:
   structure = get_file_structure("file.py")
   # Now know exactly where to put code
   ```

2. **Make focused changes**
   ```python
   # Instead of inserting 100 lines
   # Insert one function at a time
   ```

3. **Split large changes into steps**
   ```python
   # Step 1: Add imports
   # Step 2: Add helper functions
   # Step 3: Add main function
   ```

4. **Use chunking for multi-function files**
   ```python
   # If adding multiple functions, chunk them
   chunks = split_large_insertion(functions, chunk_size=2000)
   ```

### ❌ DON'T:

1. **Don't insert entire files at once**
   ```python
   # Bad:
   insert_text("new_file.py", 1, entire_module_code)
   
   # Good:
   insert_text("new_file.py", 1, function1)
   insert_text("new_file.py", 20, function2)
   ```

2. **Don't ignore JSON size estimates**
   ```python
   # Check size first
   estimated = estimate_json_size(text)
   if estimated > 50KB:
      # Use chunking
   ```

3. **Don't create code from scratch for large files**
   ```python
   # Bad: Agent generates 500-line file
   # Good: Agent generates small pieces and inserts them
   ```

## Limits

| Item | Limit | Solution |
|------|-------|----------|
| Single insertion | 100KB | Use chunking |
| Total tool call | 500KB | Split into multiple calls |
| File read | 10MB | Use `max_lines` or `get_file_structure()` |
| JSON overhead | ~20% | Account for escaping |

## Error Recovery

If you see JSON errors:

### "Invalid JSON: EOF while parsing"
- **Cause**: JSON got truncated
- **Fix**: Check if you're inserting large text (>2KB)
- **Action**: Use chunking or split into smaller changes

### "input: Invalid JSON: Unexpected character"
- **Cause**: Special characters not properly escaped
- **Fix**: Check for quotes, backslashes, control characters
- **Action**: Use proper string escaping

### "Tool call too large"
- **Cause**: Parameters exceed 100KB
- **Fix**: Split into multiple tool calls
- **Action**: Use chunking utility

## Debugging

Enable validation to catch issues early:

```python
from src.tools.validation import ToolValidator

# Validate before sending
is_valid, error = ToolValidator.validate_insert_tool(
    filepath="file.py",
    line_number=1,
    text=code
)

if not is_valid:
    print(f"Parameter error: {error}")
    # Can use split_large_insertion here
```

## Implementation in Agent

When using pydantic-ai, the agent should:

1. **Check file structure first** - Understand what to change
2. **Validate parameters** - Use ToolValidator before calling tools
3. **Use chunking automatically** - Large insertions handled transparently
4. **Provide recovery suggestions** - Tell user how to fix issues

Example agent setup:

```python
from pydantic_ai import Agent
from src.tools.file_tools import FileTool
from src.tools.validation import ToolValidator

agent = Agent()

@agent.tool
async def insert(filepath: str, line_number: int, text: str) -> str:
    # Validate first
    is_valid, error = ToolValidator.validate_insert_tool(filepath, line_number, text)
    if not is_valid:
        return f"Error: {error}"
    
    # Tool handles chunking automatically
    result = FileTool.insert_text(filepath, line_number, text)
    return result['message']

@agent.tool
async def understand_file(filepath: str) -> str:
    # Use this before inserting
    structure = FileTool.get_file_structure(filepath)
    return json.dumps(structure, indent=2)
```

## Summary

| Scenario | Solution |
|----------|----------|
| Inserting 1-10 lines | Use `insert` directly |
| Inserting 10-50 lines | Still use `insert` directly, it auto-chunks |
| Inserting 50+ lines | Use `understand_file` first, then insert in pieces |
| Unknown file | Use `understand_file` first |
| Inserting >100KB | Definitely chunk, or reconsider approach |
| JSON error | Check parameter sizes, enable validation |

