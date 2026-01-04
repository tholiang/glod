#!/usr/bin/env python3
"""
Test script for code understanding tools implementation
"""
import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Set up environment
os.chdir(Path(__file__).parent)

from server.app import get_app
from server.tools import code_understanding

# Setup allowed paths for testing
app = get_app()
app.allow_path(Path('.').resolve())

def test_get_file_structure():
    """Test get_file_structure tool"""
    print("=" * 60)
    print("TEST: get_file_structure")
    print("=" * 60)
    print("Analyzing src/server/app.py...")
    result = code_understanding.get_file_structure("src/server/app.py")
    print("Result:")
    print(result)
    
    # Verify it's valid JSON with expected keys
    try:
        data = json.loads(result)
        has_functions = 'functions' in data
        has_classes = 'classes' in data
        has_file = 'file' in data
        success = has_functions and has_classes and has_file
        print(f"\nValid JSON: ✓")
        print(f"Has 'functions' key: {'✓' if has_functions else '✗'}")
        print(f"Has 'classes' key: {'✓' if has_classes else '✗'}")
        print(f"Has 'file' key: {'✓' if has_file else '✗'}")
        return success
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return False

def test_trace_call_chain():
    """Test trace_call_chain tool"""
    print("\n" + "=" * 60)
    print("TEST: trace_call_chain")
    print("=" * 60)
    print("Tracing get_app function in src/server/app.py...")
    result = code_understanding.trace_call_chain("get_app", "src/server/app.py")
    print("Result:")
    print(result)
    
    # Verify it's valid JSON with expected keys
    try:
        data = json.loads(result)
        has_function = 'function' in data
        has_callers = 'callers' in data
        has_callees = 'callees' in data
        success = has_function and has_callers and has_callees
        print(f"\nValid JSON: ✓")
        print(f"Has 'function' key: {'✓' if has_function else '✗'}")
        print(f"Has 'callers' key: {'✓' if has_callers else '✗'}")
        print(f"Has 'callees' key: {'✓' if has_callees else '✗'}")
        return success
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return False

def test_analyze_imports():
    """Test analyze_imports tool"""
    print("\n" + "=" * 60)
    print("TEST: analyze_imports")
    print("=" * 60)
    print("Analyzing imports in src/server/agents/editor.py...")
    result = code_understanding.analyze_imports("src/server/agents/editor.py")
    print("Result:")
    print(result)
    
    # Verify it's valid JSON with expected keys
    try:
        data = json.loads(result)
        has_file = 'file' in data
        has_total = 'total_imports' in data
        has_regular = 'regular_imports' in data
        has_from = 'from_imports' in data
        success = has_file and has_total and has_regular and has_from
        print(f"\nValid JSON: ✓")
        print(f"Has 'file' key: {'✓' if has_file else '✗'}")
        print(f"Has 'total_imports' key: {'✓' if has_total else '✗'}")
        print(f"Has 'regular_imports' key: {'✓' if has_regular else '✗'}")
        print(f"Has 'from_imports' key: {'✓' if has_from else '✗'}")
        return success
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return False

def test_get_type_info():
    """Test get_type_info tool"""
    print("\n" + "=" * 60)
    print("TEST: get_type_info")
    print("=" * 60)
    print("Getting type info for 'get_app' function in src/server/app.py...")
    result = code_understanding.get_type_info("src/server/app.py", "get_app")
    print("Result:")
    print(result)
    
    # Verify it's valid JSON with expected keys
    try:
        data = json.loads(result)
        has_file = 'file' in data
        has_symbol = 'symbol' in data
        has_found = 'found' in data
        success = has_file and has_symbol and has_found
        print(f"\nValid JSON: ✓")
        print(f"Has 'file' key: {'✓' if has_file else '✗'}")
        print(f"Has 'symbol' key: {'✓' if has_symbol else '✗'}")
        print(f"Has 'found' key: {'✓' if has_found else '✗'}")
        if data.get('found'):
            print(f"Symbol found: ✓ (type: {data.get('type')})")
        return success
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return False

def test_get_class_type_info():
    """Test get_type_info tool on a class"""
    print("\n" + "=" * 60)
    print("TEST: get_type_info (class)")
    print("=" * 60)
    print("Getting type info for 'App' class in src/server/app.py...")
    result = code_understanding.get_type_info("src/server/app.py", "App")
    print("Result:")
    print(result)
    
    # Verify it's valid JSON
    try:
        data = json.loads(result)
        found = data.get('found')
        if found:
            print(f"Class found: ✓ (type: {data.get('type')})")
        return True
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        return False

def test_pydantic_tools():
    """Test that pydantic tools are correctly exported"""
    print("\n" + "=" * 60)
    print("TEST: pydantic tools export")
    print("=" * 60)
    tools = code_understanding.get_pydantic_tools()
    print(f"Number of tools exported: {len(tools)}")
    for tool in tools:
        print(f"  - {tool.function.name}")
    print()
    return len(tools) == 4

if __name__ == "__main__":
    tests = [
        ("get_file_structure", test_get_file_structure),
        ("trace_call_chain", test_trace_call_chain),
        ("analyze_imports", test_analyze_imports),
        ("get_type_info", test_get_type_info),
        ("get_type_info (class)", test_get_class_type_info),
        ("pydantic_tools", test_pydantic_tools),
    ]
    
    results = {}
    try:
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"ERROR in {test_name}: {e}")
                import traceback
                traceback.print_exc()
                results[test_name] = False
        
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        for test_name, passed in results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{status}: {test_name}")
        
        all_passed = all(results.values())
        if all_passed:
            print("\nAll tests passed!")
            sys.exit(0)
        else:
            print("\nSome tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"Fatal error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
