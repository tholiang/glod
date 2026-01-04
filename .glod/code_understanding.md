# Code Understanding Tools

Tools for analyzing Python code structure, imports, and type information without reading full source files.

## Tools

### get_file_structure(file_path)
Returns JSON with functions and classes in a file. Each function includes:
- `lineno`: Line number
- `signature`: Full function signature with types
- `docstring`: Function docstring
- `type_hints`: Dict of parameter types and return type

Each class includes:
- `lineno`: Line number
- `methods`: List of methods with signatures
- `base_classes`: Parent class names
- `docstring`: Class docstring

### trace_call_chain(function_name, file_path)
Returns caller/callee relationships for a function:
- `callers`: Functions that call this function
- `callees`: Functions this function calls

Built using AST visitor that tracks function calls within each function body.

### analyze_imports(file_path)
Returns all imports grouped by type:
- `regular_imports`: `import x` statements
- `from_imports`: `from x import y` statements

Each import includes module name, alias, and level (for relative imports).

### get_type_info(file_path, symbol_name)
Returns type hints for a function or class:
- For functions: signature, parameter types, return type, docstring
- For classes: methods, base classes, docstring

## Implementation

Uses Python `ast` module to parse code without executing. CodeAnalyzer visitor extracts:
- All function/method definitions
- All class definitions
- Import statements
- Call graph (who calls whom)

All functions return JSON for consistent handling and easy parsing.
