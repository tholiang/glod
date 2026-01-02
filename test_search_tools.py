#!/usr/bin/env python3
"""
Test script for search tools implementation
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Set up environment
os.chdir(Path(__file__).parent)

from server.app import get_app
from server.tools import search

# Setup allowed paths for testing
app = get_app()
app.allow_path(Path('.').resolve())

def test_search_code():
    """Test search_code tool"""
    print("=" * 60)
    print("TEST: search_code")
    print("=" * 60)
    print("Searching for 'def get_pydantic_tools'...")
    result = search.search_code("def get_pydantic", [".py"])
    print("Result:")
    print(result)
    print()
    return "error" not in result.lower()

def test_find_symbol():
    """Test find_symbol tool"""
    print("=" * 60)
    print("TEST: find_symbol")
    print("=" * 60)
    print("Looking for symbol 'get_app'...")
    result = search.find_symbol("get_app")
    print("Result:")
    print(result)
    print()
    return "error" not in result.lower()

def test_get_dependencies():
    """Test get_dependencies tool"""
    print("=" * 60)
    print("TEST: get_dependencies")
    print("=" * 60)
    print("Getting dependencies for src/server/tools/search.py...")
    result = search.get_dependencies("src/server/tools/search.py")
    print("Result:")
    print(result)
    print()
    return "error" not in result.lower() and "import" in result.lower()

def test_find_references():
    """Test find_references tool"""
    print("=" * 60)
    print("TEST: find_references")
    print("=" * 60)
    print("Looking for references to 'Agent'...")
    result = search.find_references("Agent")
    print("Result:")
    print(result[:500] + "..." if len(result) > 500 else result)  # Truncate long output
    print()
    return "error" not in result.lower()

def test_pydantic_tools():
    """Test that pydantic tools are correctly exported"""
    print("=" * 60)
    print("TEST: pydantic tools export")
    print("=" * 60)
    tools = search.get_pydantic_search_tools()
    print(f"Number of tools exported: {len(tools)}")
    for tool in tools:
        print(f"  - {tool.function.name}")
    print()
    return len(tools) == 4

if __name__ == "__main__":
    tests = [
        ("search_code", test_search_code),
        ("find_symbol", test_find_symbol),
        ("get_dependencies", test_get_dependencies),
        ("find_references", test_find_references),
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
        print("=" * 60)
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

