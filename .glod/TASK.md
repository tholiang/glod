You are working on GLOD, a coding agent framework. Your task is to implement the 
HIGH PRIORITY enhancements from .glod/todo.md. Focus on these three categories:

### HIGH PRIORITY TASKS (Complete these):

1. **Search/Context Tools** - Code search, symbol finding, dependency analysis
   - Tools: search_code(), find_symbol(), get_dependencies(), find_references()
   
2. **Code Understanding Tools** - AST analysis, call graphs, type information
   - Tools: get_file_structure(), trace_call_chain()
   
3. **Test & Validation Tools** - Test runner, linting, syntax checking
   - Tools: run_tests(), lint_file(), check_syntax()

### TASK DEPENDENCIES:

- Tasks 1 & 2 are INDEPENDENT - can be done in parallel
- Task 3 is INDEPENDENT - can be done in parallel
- All three tasks should use ripgrep for code search and AST parsing for Python analysis

### WORKFLOW:

1. Create three git branches:
   - `feature/search-context-tools` (for Task 1)
   - `feature/code-understanding-tools` (for Task 2)
   - `feature/test-validation-tools` (for Task 3)

2. Spawn three subagents (one per branch):
   - Subagent 1: Implement search/context tools on `feature/search-context-tools`
   - Subagent 2: Implement code understanding tools on `feature/code-understanding-tools`
   - Subagent 3: Implement test/validation tools on `feature/test-validation-tools`

3. Each subagent should:
   - Work only on their assigned branch
   - Read .glod/overview.md to understand the project
   - Implement their assigned tools with proper error handling
   - Update .glod/ documentation if creating new major features
   - Commit their work with clear commit messages

### NOTES:
- See .glod/overview.md for current architecture
- Tools should integrate with existing GLOD tool framework
- Prioritize ripgrep for fast code search and Python ast module for parsing
- Each tool should be well-tested before commit