def test_extract_functions_from_code(code: str):
    tree = ast.parse(code)
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

def test_analyze_ast_diff(before_code: str, after_code: str):
    before_funcs = set(extract_functions_from_code(before_code))
    after_funcs = set(extract_functions_from_code(after_code))
    added = after_funcs - before_funcs
    removed = before_funcs - after_funcs
    return {"added": list(added), "removed": list(removed)}