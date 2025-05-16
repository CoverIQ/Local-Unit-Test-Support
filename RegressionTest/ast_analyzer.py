import ast
from typing import List, Dict, Tuple,Set

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

    # 🧠 Find indirect dependents (functions that call modified ones)
    call_graph = build_call_graph(after_code)
    indirect_dependents = find_callers(modified, call_graph)

    return {
        "added": list(added),
        "removed": list(removed),
        "modified": modified,
        "indirect_dependents": list(indirect_dependents)
    }



if __name__ == "__main__":
    before_code = """
def foo():
    bar()
    helper()

def bar():
    print("bar")

def helper():
    pass
"""

    after_code = """
def foo():
    bar()
    x.baz()
    helper()

def bar():
    print("bar changed")

def helper():
    pass

class MyClass:
    def method(self):
        helper()
        self.other()

    def other(self):
        pass
"""

    result = analyze_ast_diff(before_code, after_code)
    print("Analysis Result:")
    for key, val in result.items():
        print(f"{key}: {val}")