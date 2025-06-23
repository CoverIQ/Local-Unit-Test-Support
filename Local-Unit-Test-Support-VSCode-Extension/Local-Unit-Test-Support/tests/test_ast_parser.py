import pytest
from pathlib import Path
from ast_parser import (
    extract_functions_with_body,
    build_call_graph,
    find_callers,
    analyze_ast_diff,
    extract_code_blocks
)

def test_extract_functions_with_body():
    """Test extracting functions with their bodies."""
    code = """
def func1():
    pass

def func2():
    x = 1
    return x
    """
    functions = extract_functions_with_body(code)
    assert len(functions) == 2
    assert "func1" in functions
    assert "func2" in functions
    assert "def func1():\n    pass" in functions["func1"]
    assert "def func2():\n    x = 1\n    return x" in functions["func2"]

def test_build_call_graph():
    """Test building call graph from code."""
    code = """
def func1():
    func2()
    func3()

def func2():
    pass

def func3():
    func2()
    """
    call_graph = build_call_graph(code)
    assert "func1" in call_graph
    assert "func2" in call_graph
    assert "func3" in call_graph
    assert call_graph["func1"] == {"func2", "func3"}
    assert call_graph["func2"] == set()
    assert call_graph["func3"] == {"func2"}

def test_find_callers():
    """Test finding callers of target functions."""
    call_graph = {
        "func1": {"func2", "func3"},
        "func2": {"func4"},
        "func3": {"func2"},
        "func4": set()
    }
    target_funcs = ["func2"]
    callers = find_callers(target_funcs, call_graph)
    assert callers == {"func1", "func3"}

def test_analyze_ast_diff():
    """Test analyzing AST differences between two code versions."""
    before_code = """
def func1():
    pass

def func2():
    x = 1
    return x
    """
    after_code = """
def func1():
    return True

def func3():
    pass
    """
    changes = analyze_ast_diff(before_code, after_code)
    assert "modified" in changes
    assert "removed" in changes
    assert "added" in changes
    assert "func1" in changes["modified"]
    assert "func2" in changes["removed"]
    assert "func3" in changes["added"]

def test_extract_code_blocks(tmp_path):
    """Test extracting code blocks from a file."""
    test_file = tmp_path / "test_file.py"
    test_file.write_text("""
class TestClass:
    def method1(self):
        pass

def func1():
    pass
    """)
    
    code_blocks = extract_code_blocks(test_file, str(tmp_path))
    assert len(code_blocks) == 2
    assert any("TestClass" in block["code"] for block in code_blocks.values())
    assert any("func1" in block["code"] for block in code_blocks.values())

def test_extract_code_blocks_with_imports(tmp_path):
    """Test extracting code blocks with imports."""
    test_file = tmp_path / "test_file.py"
    test_file.write_text("""
import os
from pathlib import Path

def func1():
    pass
    """)
    
    code_blocks = extract_code_blocks(test_file, str(tmp_path))
    assert len(code_blocks) == 1
    assert "func1" in next(iter(code_blocks.values()))["code"] 