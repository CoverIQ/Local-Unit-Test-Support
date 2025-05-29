import os,ast
from collections import defaultdict

def extract_called_functions_from_test(code: str) -> set:
    class CallVisitor(ast.NodeVisitor):
        def __init__(self):
            self.called_funcs = set()
        
        def visit_Call(self, node):
            if isinstance(node.func, ast.Name):
                self.called_funcs.add(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                self.called_funcs.add(node.func.attr)
            self.generic_visit(node)

    tree = ast.parse(code)
    visitor = CallVisitor()
    visitor.visit(tree)
    return visitor.called_funcs

def guess_related_tests(changed_functions: list, test_dir: str) -> list:
    related_tests = []
    for root, _, files in os.walk(test_dir):
        for f in files:
            if f.startswith("test_") and f.endswith(".py"):
                with open(os.path.join(root, f)) as tf:
                    content = tf.read()
                    for func in changed_functions:
                        if func in content:
                            related_tests.append(f)
                            break
    return related_tests


def extract_call_graph(code: str) -> dict[str, set[str]]:
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
    return collector.calls

def expand_calls(call_map: dict[str, set[str]]) -> dict[str, set[str]]:
    def dfs(func, visited):
        for callee in call_map.get(func, []):
            if callee not in visited:
                visited.add(callee)
                dfs(callee, visited)
        return visited

    return {func: dfs(func, set()) for func in call_map}