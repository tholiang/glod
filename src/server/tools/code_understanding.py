"""
Code understanding tools for analyzing Python code structure, imports, and type information.

Provides analysis capabilities:
- get_file_structure: Extract functions/classes/signatures without full code
- trace_call_chain: Show which functions call a function and which it calls
- analyze_imports: Extract and analyze imports in a file
- get_type_info: Extract type hints for symbols
"""
import ast
import json
from typing import Dict, List, Optional

from pydantic_ai import Tool

from server.tools.util import _check_access


class CodeAnalyzer(ast.NodeVisitor):
    """Visitor to analyze Python code structure"""
    
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.functions = {}
        self.classes = {}
        self.imports = []
        self.call_graph = {}  # Maps function names to functions they call
        self.called_by = {}   # Maps function names to functions that call them
        self.type_hints = {}  # Maps symbols to their type hints
        self.current_function = None
        
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions"""
        signature = self._get_function_signature(node)
        self.functions[node.name] = {
            'lineno': node.lineno,
            'signature': signature,
            'docstring': ast.get_docstring(node),
            'type_hints': self._extract_type_hints(node),
        }
        
        # Track calls within this function
        old_function = self.current_function
        self.current_function = node.name
        self.call_graph[node.name] = []
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions"""
        signature = self._get_function_signature(node)
        self.functions[node.name] = {
            'lineno': node.lineno,
            'signature': signature,
            'docstring': ast.get_docstring(node),
            'type_hints': self._extract_type_hints(node),
            'is_async': True,
        }
        
        old_function = self.current_function
        self.current_function = node.name
        self.call_graph[node.name] = []
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions"""
        self.classes[node.name] = {
            'lineno': node.lineno,
            'docstring': ast.get_docstring(node),
            'methods': [],
            'base_classes': [ast.unparse(base) if hasattr(ast, 'unparse') else 'Unknown' for base in node.bases],
        }
        
        # Extract methods
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method_sig = self._get_function_signature(item)
                self.classes[node.name]['methods'].append({
                    'name': item.name,
                    'signature': method_sig,
                    'docstring': ast.get_docstring(item),
                    'type_hints': self._extract_type_hints(item),
                })
        
        self.generic_visit(node)
    
    def visit_Import(self, node: ast.Import) -> None:
        """Visit import statements"""
        for alias in node.names:
            self.imports.append({
                'type': 'import',
                'module': alias.name,
                'alias': alias.asname,
            })
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Visit from...import statements"""
        for alias in node.names:
            self.imports.append({
                'type': 'from',
                'module': node.module or '',
                'name': alias.name,
                'alias': alias.asname,
                'level': node.level,  # For relative imports
            })
        self.generic_visit(node)
    
    def visit_Call(self, node: ast.Call) -> None:
        """Visit function calls to build call graph"""
        if self.current_function:
            # Extract the called function name
            called_name = self._get_call_name(node.func)
            if called_name:
                if called_name not in self.call_graph[self.current_function]:
                    self.call_graph[self.current_function].append(called_name)
                
                # Track reverse mapping
                if called_name not in self.called_by:
                    self.called_by[called_name] = []
                if self.current_function not in self.called_by[called_name]:
                    self.called_by[called_name].append(self.current_function)
        
        self.generic_visit(node)
    
    def _get_function_signature(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Extract function signature with parameters and return type"""
        try:
            # Use ast.unparse if available (Python 3.9+)
            if hasattr(ast, 'unparse'):
                return ast.unparse(node)[:200]  # Limit to 200 chars
            
            # Fallback: manual signature construction
            args = node.args
            params = []
            
            # Regular arguments
            for arg in args.args:
                annotation = ''
                if arg.annotation:
                    annotation = f': {ast.unparse(arg.annotation)}'
                params.append(f'{arg.arg}{annotation}')
            
            # Keyword-only arguments
            for arg in args.kwonlyargs:
                annotation = ''
                if arg.annotation:
                    annotation = f': {ast.unparse(arg.annotation)}'
                params.append(f'{arg.arg}{annotation}')
            
            return_type = ''
            if node.returns:
                return_type = f' -> {ast.unparse(node.returns)}'
            
            return f"def {node.name}({', '.join(params)}){return_type}"
        except Exception:
            return f"def {node.name}(...)"
    
    def _extract_type_hints(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> Dict[str, str]:
        """Extract type hints from function arguments and return type"""
        hints = {}
        
        # Extract argument type hints
        for arg in node.args.args:
            if arg.annotation:
                hints[arg.arg] = ast.unparse(arg.annotation) if hasattr(ast, 'unparse') else 'annotation'
        
        # Extract return type hint
        if node.returns:
            hints['return'] = ast.unparse(node.returns) if hasattr(ast, 'unparse') else 'annotation'
        
        return hints
    
    def _get_call_name(self, node: ast.expr) -> Optional[str]:
        """Extract the name of a called function"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # For method calls like obj.method()
            return node.attr
        elif isinstance(node, ast.Call):
            return self._get_call_name(node.func)
        return None


def get_file_structure(file_path: str) -> str:
    """
    Extract functions, classes, and their signatures from a Python file without full code.
    
    Args:
        file_path: Path to the Python file to analyze
    
    Returns:
        JSON string containing file structure with functions and classes
    """
    if not _check_access(file_path):
        return json.dumps({"error": "access denied to this path"})
    
    try:
        with open(file_path, 'r') as f:
            source_code = f.read()
        
        tree = ast.parse(source_code)
        analyzer = CodeAnalyzer(source_code)
        analyzer.visit(tree)
        
        structure = {
            'file': file_path,
            'functions': analyzer.functions,
            'classes': analyzer.classes,
        }
        
        return json.dumps(structure, indent=2, default=str)
    except SyntaxError as e:
        return json.dumps({"error": f"syntax error: {e}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def trace_call_chain(function_name: str, file_path: Optional[str] = None) -> str:
    """
    Trace which functions call a given function and which it calls.
    
    Args:
        function_name: Name of the function to trace
        file_path: Optional specific file to analyze. If not provided, searches current file.
    
    Returns:
        JSON string showing callers and callees
    """
    if file_path and not _check_access(file_path):
        return json.dumps({"error": "access denied to this path"})
    
    try:
        # If file_path is provided, analyze just that file
        if file_path:
            with open(file_path, 'r') as f:
                source_code = f.read()
            
            tree = ast.parse(source_code)
            analyzer = CodeAnalyzer(source_code)
            analyzer.visit(tree)
            
            result = {
                'function': function_name,
                'file': file_path,
                'callers': analyzer.called_by.get(function_name, []),
                'callees': analyzer.call_graph.get(function_name, []),
            }
            
            return json.dumps(result, indent=2)
        else:
            return json.dumps({"error": "file_path is required for trace_call_chain"})
    
    except SyntaxError as e:
        return json.dumps({"error": f"syntax error: {e}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def analyze_imports(file_path: str) -> str:
    """
    Extract and analyze all imports in a Python file.
    
    Args:
        file_path: Path to the Python file to analyze
    
    Returns:
        JSON string containing all imports grouped by type
    """
    if not _check_access(file_path):
        return json.dumps({"error": "access denied to this path"})
    
    try:
        with open(file_path, 'r') as f:
            source_code = f.read()
        
        tree = ast.parse(source_code)
        analyzer = CodeAnalyzer(source_code)
        analyzer.visit(tree)
        
        # Group imports by type
        regular_imports = [imp for imp in analyzer.imports if imp['type'] == 'import']
        from_imports = [imp for imp in analyzer.imports if imp['type'] == 'from']
        
        result = {
            'file': file_path,
            'total_imports': len(analyzer.imports),
            'regular_imports': regular_imports,
            'from_imports': from_imports,
        }
        
        return json.dumps(result, indent=2, default=str)
    except SyntaxError as e:
        return json.dumps({"error": f"syntax error: {e}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_type_info(file_path: str, symbol_name: str) -> str:
    """
    Extract type hints for a specific symbol (function, class, variable).
    
    Args:
        file_path: Path to the Python file to analyze
        symbol_name: Name of the symbol to get type info for
    
    Returns:
        JSON string containing type information for the symbol
    """
    if not _check_access(file_path):
        return json.dumps({"error": "access denied to this path"})
    
    try:
        with open(file_path, 'r') as f:
            source_code = f.read()
        
        tree = ast.parse(source_code)
        analyzer = CodeAnalyzer(source_code)
        analyzer.visit(tree)
        
        result = {
            'file': file_path,
            'symbol': symbol_name,
            'found': False,
            'type_hints': {},
        }
        
        # Check if it's a function
        if symbol_name in analyzer.functions:
            func_info = analyzer.functions[symbol_name]
            result['found'] = True
            result['type'] = 'function'
            result['signature'] = func_info['signature']
            result['type_hints'] = func_info['type_hints']
            result['docstring'] = func_info.get('docstring')
        
        # Check if it's a class
        elif symbol_name in analyzer.classes:
            class_info = analyzer.classes[symbol_name]
            result['found'] = True
            result['type'] = 'class'
            result['base_classes'] = class_info['base_classes']
            result['docstring'] = class_info.get('docstring')
            result['methods'] = class_info['methods']
        
        return json.dumps(result, indent=2, default=str)
    except SyntaxError as e:
        return json.dumps({"error": f"syntax error: {e}"})
    except Exception as e:
        return json.dumps({"error": str(e)})


def get_pydantic_tools() -> List[Tool]:
    """Get all code understanding tools as pydantic-ai Tool objects"""
    return [
        Tool(get_file_structure, takes_ctx=False),
        Tool(trace_call_chain, takes_ctx=False),
        Tool(analyze_imports, takes_ctx=False),
        Tool(get_type_info, takes_ctx=False),
    ]
