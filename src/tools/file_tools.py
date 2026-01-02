"""
Enhanced file tools with better error handling and validation.

Replaces/supplements basic file operations with:
- Size validation before operations
- Better error messages
- Support for chunked insertions
- Automatic error recovery
"""
from pathlib import Path
from typing import Optional
import sys
from .chunking import split_large_insertion, validate_json_serializable, estimate_json_size


class FileTool:
    """Safe file operations with validation and error handling."""
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_INSERTION_SIZE = 500 * 1024  # 500KB per insertion
    
    @staticmethod
    def _check_file_size(filepath: str) -> tuple[bool, Optional[str]]:
        """Check if file is readable and not too large."""
        try:
            path = Path(filepath)
            if not path.exists():
                return True, None  # File doesn't exist, that's ok
            
            size = path.stat().st_size
            if size > FileTool.MAX_FILE_SIZE:
                return False, f"File too large: {size} bytes (max {FileTool.MAX_FILE_SIZE})"
            
            return True, None
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def read_file(filepath: str, max_lines: Optional[int] = None) -> dict:
        """
        Read a file with error handling.
        
        Returns:
            {"status": "success"|"error", "content": str, "error": str, "size": int}
        """
        try:
            ok, err = FileTool._check_file_size(filepath)
            if not ok:
                return {"status": "error", "error": err, "content": "", "size": 0}
            
            path = Path(filepath)
            content = path.read_text(encoding='utf-8')
            
            if max_lines:
                lines = content.split('\n')
                content = '\n'.join(lines[:max_lines])
            
            return {
                "status": "success",
                "content": content,
                "error": None,
                "size": len(content.encode('utf-8'))
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "content": "",
                "size": 0
            }
    
    @staticmethod
    def insert_text(filepath: str, line_number: int, text: str) -> dict:
        """
        Insert text at a specific line.
        
        For large insertions (>2KB), automatically chunks the insertion.
        
        Returns:
            {"status": "success"|"error", "message": str, "chunks": int}
        """
        try:
            # Validate insertion size
            json_size = estimate_json_size(text)
            if json_size > FileTool.MAX_INSERTION_SIZE:
                # Need to chunk
                chunks = split_large_insertion(text, chunk_size=2000)
                
                path = Path(filepath)
                
                # Read existing content
                if path.exists():
                    content = path.read_text(encoding='utf-8')
                    lines = content.split('\n')
                else:
                    lines = []
                
                # Insert all chunks
                for i, chunk in enumerate(chunks):
                    insertion_line = line_number + i
                    lines.insert(insertion_line - 1, chunk['text'].rstrip('\n'))
                
                # Write back
                path.write_text('\n'.join(lines), encoding='utf-8')
                
                return {
                    "status": "success",
                    "message": f"Inserted {len(chunks)} chunks into {filepath} at line {line_number}",
                    "chunks": len(chunks)
                }
            
            # Single insertion
            path = Path(filepath)
            if path.exists():
                content = path.read_text(encoding='utf-8')
                lines = content.split('\n')
            else:
                lines = []
            
            # Insert before the specified line
            lines.insert(line_number - 1, text)
            path.write_text('\n'.join(lines), encoding='utf-8')
            
            return {
                "status": "success",
                "message": f"Inserted text into {filepath} at line {line_number}",
                "chunks": 1
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to insert text: {str(e)}",
                "chunks": 0
            }
    
    @staticmethod
    def delete_lines(filepath: str, start_line: int, end_line: int) -> dict:
        """Delete lines from a file."""
        try:
            path = Path(filepath)
            if not path.exists():
                return {"status": "error", "message": f"File not found: {filepath}"}
            
            content = path.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            # Delete lines (1-indexed, inclusive)
            del lines[start_line - 1:end_line]
            
            path.write_text('\n'.join(lines), encoding='utf-8')
            
            return {
                "status": "success",
                "message": f"Deleted lines {start_line}-{end_line} from {filepath}",
                "lines_deleted": end_line - start_line + 1
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to delete lines: {str(e)}"
            }
    
    @staticmethod
    def get_file_structure(filepath: str) -> dict:
        """
        Get the structure of a Python file (functions, classes, line numbers).
        
        Helps agent understand file without reading entire content.
        """
        try:
            import ast
            
            path = Path(filepath)
            if not path.exists():
                return {"status": "error", "message": f"File not found: {filepath}"}
            
            content = path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            structure = {
                "status": "success",
                "file": filepath,
                "classes": [],
                "functions": [],
                "imports": []
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    structure["classes"].append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [
                            n.name for n in node.body 
                            if isinstance(n, ast.FunctionDef)
                        ]
                    })
                elif isinstance(node, ast.FunctionDef):
                    if not any(isinstance(p, ast.ClassDef) for p in ast.walk(tree)):
                        structure["functions"].append({
                            "name": node.name,
                            "line": node.lineno,
                            "args": [arg.arg for arg in node.args.args]
                        })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        structure["imports"].append({
                            "module": node.names[0].name,
                            "line": node.lineno
                        })
                    else:
                        structure["imports"].append({
                            "module": node.module,
                            "line": node.lineno
                        })
            
            return structure
        
        except SyntaxError as e:
            return {
                "status": "error",
                "message": f"Syntax error in {filepath}: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to analyze structure: {str(e)}"
            }

