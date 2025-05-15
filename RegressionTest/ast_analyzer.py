import ast
from typing import List, Dict, Tuple

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

    return {
        "added": list(added),
        "removed": list(removed),
        "modified": modified
    }