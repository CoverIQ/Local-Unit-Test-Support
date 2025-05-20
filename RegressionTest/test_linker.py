import os,ast

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