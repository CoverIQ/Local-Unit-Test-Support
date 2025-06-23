import ast
from typing import List, Dict, Set
from pathlib import Path
from collections import defaultdict

def extract_functions_with_body(code: str) -> Dict[str, str]:
    """
    Extract function names and their source code body from Python code.
    """
    tree = ast.parse(code)
    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Use the full function body as the value
            func_name = node.name
            func_code = ast.unparse(node)  # Requires Python 3.9+
            functions[func_name] = func_code
    return functions

def extract_call_graph(code: str) -> Dict[str, Set[str]]:
    """
    Extract a call graph from Python code.
    Returns a dictionary mapping function names to sets of functions they call.
    """
    class FunctionCallCollector(ast.NodeVisitor):
        def __init__(self):
            self.calls = defaultdict(set)
            self.current_func = None

        def visit_FunctionDef(self, node):
            self.current_func = node.name
            self.generic_visit(node)
            self.current_func = None

        def visit_Call(self, node):
            if self.current_func:
                if isinstance(node.func, ast.Name):
                    self.calls[self.current_func].add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    self.calls[self.current_func].add(node.func.attr)
            self.generic_visit(node)

    tree = ast.parse(code)
    collector = FunctionCallCollector()
    collector.visit(tree)
    return dict(collector.calls)

def build_call_graph(code: str) -> Dict[str, Set[str]]:
    """
    Build a call graph: {caller_function: set(called_function_names)}
    """
    call_graph = {}

    class FunctionVisitor(ast.NodeVisitor):
        def __init__(self):
            self.current_func = None

        def visit_FunctionDef(self, node: ast.FunctionDef):
            self.current_func = node.name
            call_graph[self.current_func] = set()
            self.generic_visit(node)
            self.current_func = None

        def visit_Call(self, node: ast.Call):
            if self.current_func:
                if isinstance(node.func, ast.Name):
                    call_graph[self.current_func].add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    call_graph[self.current_func].add(node.func.attr)
            self.generic_visit(node)

    tree = ast.parse(code)
    FunctionVisitor().visit(tree)
    return call_graph

def find_callers(target_funcs: List[str], call_graph: Dict[str, Set[str]]) -> Set[str]:
    """
    Return all functions that call any of the target functions.
    """
    callers = set()
    for caller, callees in call_graph.items():
        if any(target in callees for target in target_funcs):
            callers.add(caller)
    return callers

def expand_calls(call_map: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    """
    Expand the call graph to include all functions that are called transitively.
    For each function, returns the set of all functions it calls directly or indirectly.
    """
    def dfs(func: str, visited: Set[str]) -> Set[str]:
        for callee in call_map.get(func, []):
            if callee not in visited:
                visited.add(callee)
                dfs(callee, visited)
        return visited

    return {func: dfs(func, set()) for func in call_map}

def analyze_ast_diff(before_code: str, after_code: str) -> Dict[str, List[str]]:
    before_funcs = extract_functions_with_body(before_code)
    after_funcs = extract_functions_with_body(after_code)

    before_names = set(before_funcs.keys())
    after_names = set(after_funcs.keys())

    added = after_names - before_names
    removed = before_names - after_names

    modified = []
    for func_name in before_names & after_names:
        if before_funcs[func_name] != after_funcs[func_name]:
            modified.append(func_name)

    # Find indirect dependents (functions that call modified ones)
    call_graph = build_call_graph(after_code)
    indirect_dependents = find_callers(modified, call_graph)

    return {
        "added": list(added),
        "removed": list(removed),
        "modified": modified,
        "indirect_dependents": list(indirect_dependents)
    }

def extract_code_blocks(file_path: Path, repo_path: str):
    """Extract code blocks (functions and classes) from a Python file."""
    repo_path = Path(repo_path)
    code_blocks = {}
    try:
        source = file_path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        relative_path = file_path.relative_to(repo_path)
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                block_type = "function" if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else "class"
                name = node.name
                start_line = node.lineno - 1
                end_line = node.end_lineno
                code_chunk = "\n".join(source.splitlines()[start_line:end_line])
                key = (str(relative_path), name)
                code_blocks[key] = {
                    "symbol_type": block_type,
                    "symbol_name": name,
                    "file_path": str(relative_path),
                    "code": code_chunk
                }
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
    return code_blocks 