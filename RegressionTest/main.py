import os
from diff_parser import get_changed_files, get_diff
from ast_analyzer import analyze_ast_diff
from test_linker import guess_related_tests
from llm_engine import suggest_test_changes
from reporter import generate_markdown_report

def load_file(repo_path, file_path):
    with open(os.path.join(repo_path, file_path)) as f:
        return f.read()

def main(repo_path: str, test_dir: str):
    changed_files = get_changed_files(repo_path)
    for file in changed_files:
        if not file.endswith(".py"):
            continue
        
        before_code = ""  # Optional: load from previous commit using Git
        after_code = load_file(repo_path, file)
        
        changes = analyze_ast_diff(before_code, after_code)
        related_tests = guess_related_tests(changes["added"], test_dir)
        
        suggestions = {
            func: suggest_test_changes(func, after_code)
            for func in changes["added"]
        }
        
        report = generate_markdown_report(changes, related_tests, suggestions)
        print(report)

if __name__ == "__main__":
    import sys
    main(repo_path=sys.argv[1], test_dir=sys.argv[2])
