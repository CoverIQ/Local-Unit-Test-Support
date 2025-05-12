import os

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