# GLOD Enhancement TODO

## Recommendations for Improving GLOD as a Coding Agent

### 1. Search/Context Tools ⭐ HIGH PRIORITY
Your agent currently lacks semantic understanding of large codebases.

**Add:**
- **Code search tools** (ripgrep integration) - Find functions, classes, patterns across codebase
- **AST-based code navigation** - Parse files to find symbols, dependencies, call chains
- **Codebase indexing** - Build lightweight index of: functions, classes, imports, endpoints

```python
# Example tools needed:
- search_code(pattern, file_types=[".py"])
- find_symbol(symbol_name)  # Find where a function is defined
- get_dependencies(file_path)  # What does this file depend on?
- find_references(symbol_name)  # Where is this used?
```

**Why:** Agents waste tokens explaining where things are. Direct search makes them vastly more efficient.

---

### 2. Code Understanding Tools ⭐ HIGH PRIORITY
Agent needs to understand code without reading entire files.

**Add:**
- **AST summary tool** - Get structure of a file: all functions/classes without reading full code
- **Call graph analysis** - Understand how components interact
- **Dependency graph** - Visualize module relationships
- **Type information** - Extract type hints and infer types

```python
# Example:
- get_file_structure(file_path)  # Returns: functions, classes, signatures
- trace_call_chain(function_name)  # Shows: func → calls → called_by
```

**Why:** Massive context efficiency. Agent sees patterns without drowning in code.

---

### 3. Test & Validation Tools ⭐ HIGH PRIORITY
Right now your agent changes code but can't verify it works.

**Add:**
- **Test runner** - Run tests and parse results
- **Linter integration** - Check code style, type errors
- **Quick validation** - Basic syntax checks
- **Diff preview** - Show what will change before applying

```python
# Example:
- run_tests(pattern="test_*.py")
- lint_file(file_path)
- check_syntax(code_snippet)
```

**Why:** Agents need feedback loops to learn if changes are correct. Without tests, they fly blind.

---

### 4. Project Structure Analysis ⭐ MEDIUM PRIORITY
Currently `.glod/overview.md` is manual. Make it semi-automatic.

**Add:**
- **Auto-generate overview** - Scan project and create structure doc
- **Dependency analysis** - Find circular dependencies, unused modules
- **Entry point detection** - Find main.py, setup.py, etc.
- **Architecture analyzer** - Detect MVC, layered, event-driven patterns

```python
# Example:
- analyze_project_structure()  # Returns: dirs, entry points, patterns
- detect_unused_imports(file_path)
- find_circular_dependencies()
```

**Why:** Saves manual documentation work. Helps agent understand unfamiliar projects quickly.

---

### 5. Performance & Debugging Tools ⭐ MEDIUM PRIORITY
Agent needs to understand performance characteristics.

**Add:**
- **File size analyzer** - Identify large/complex files
- **Code metrics** - Lines of code, complexity (cyclomatic)
- **Import time analysis** - Which modules are slow to import
- **Memory profiler helper** - Suggest what to profile

```python
# Example:
- get_file_metrics(file_path)  # complexity, LOC, cyclomatic
- analyze_large_files()  # Files > 500 lines
```

**Why:** Helps agent make informed decisions about refactoring/optimization.

---

### 6. Streaming & Progress Feedback ⭐ MEDIUM PRIORITY
You have streaming in client, but agent response quality could improve.

**Add:**
- **Thinking blocks** - Agent can output intermediate reasoning
- **Progress indicators** - Show what it's doing during long operations
- **Checkpoints** - Save progress during multi-step tasks
- **Error recovery** - More intelligent error handling and recovery

**Why:** Better UX. Agent can explain its reasoning. Easier to debug agent errors.

---

### 7. Project-Aware Agent Configuration ⭐ MEDIUM PRIORITY
`.glod/config.json` exists but agent doesn't use it effectively.

**Add:**
- **Load agent instructions from config** - Custom behavior per project
- **Custom tool loading** - `.glod/tools/` integration with agent
- **Convention detection** - Enforce project-specific naming, structure
- **API documentation parser** - Extract API docs into agent context

```python
# In config.json:
{
  "agent_instructions": {
    "coding_style": "PEP 8, 100 char lines",
    "must_include": "Type hints, docstrings",
    "testing": "Pytest with >90% coverage"
  },
  "excluded_dirs": ["node_modules", "__pycache__"],
  "key_files": ["src/main.py", "src/config.py"]
}
```

**Why:** Agents make fewer mistakes when they understand project conventions upfront.

---

### 8. Context Window Optimization ⭐ MEDIUM PRIORITY
Since you use HTTP + pydantic-ai, tokens are expensive.

**Add:**
- **Smart file chunking** - Read only relevant parts of large files
- **Context summarization** - Summarize files agent has already seen
- **Symbol resolution** - Look up symbol definitions on-demand instead of loading files
- **Caching layer** - Cache analysis results

**Why:** Reduce API costs and latency significantly.

---

### 9. Collaborative Features ⭐ LOW PRIORITY (Advanced)
Future enhancements for team use.

**Add:**
- **Change explanation** - Agent explains what it changed and why
- **Human-in-loop approval** - Wait for user approval before applying changes
- **Undo/rollback** - Easy way to revert changes
- **Audit trail** - Track what agent did and when

**Why:** Makes agent safer for team environments.

---

### 10. Documentation Generation ⭐ LOW PRIORITY
Help maintain project docs.

**Add:**
- **README generator** - Auto-generate from structure + overview
- **API docs generator** - Extract from docstrings/type hints
- **Changelog generator** - Track changes made by agent
- **Architecture diagram** - Visual representation of module relationships

**Why:** Keeps documentation in sync with code.

---

## Implementation Priority (Quick Wins First)

**Week 1 (Do these first):**
1. ✅ Code search + find_symbol tools (huge impact on agent capability)
2. Test runner integration (enables validation)
3. File structure summary tool (context efficiency)

**Week 2:**
4. Linting integration 
5. Code metrics/complexity analyzer
6. Better error handling

**Week 3+:**
7. Streaming/progress improvements
8. Project config integration
9. Advanced features

---

## Most Important Single Thing

If I had to pick **one thing** to add:

**→ Symbol search + code search tools**

This single addition would:
- ✅ Reduce context window usage by 50%+
- ✅ Make agent 10x faster at finding code
- ✅ Enable agent to work with huge codebases
- ✅ Unlock multiple downstream capabilities

Use `ripgrep` + simple regex for search, `ast` module for Python symbol parsing.

