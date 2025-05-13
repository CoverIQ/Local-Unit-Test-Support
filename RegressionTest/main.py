import os
from diff_parser import get_changed_files, get_diff, load_file_from_previous_commit,load_file
from ast_analyzer import analyze_ast_diff
from test_linker import guess_related_tests
from llm_engine import suggest_test_changes
from reporter import generate_markdown_report

def main(repo_path: str, test_dir: str):
    changed_files = get_changed_files(repo_path)
    for file in changed_files:
        if not file.endswith(".py"):
            continue
        
        print("current file: ", file)
        before_code = load_file_from_previous_commit(repo_path, file)
        after_code = load_file(repo_path, file)
        # print(after_code)
        changes = analyze_ast_diff(before_code, after_code)
        print(changes)
        related_tests = guess_related_tests(changes["added"], test_dir)
        
        suggestions = {
            func: suggest_test_changes(func, after_code)
            for func in changes["added"]
        }
        
        report = generate_markdown_report(changes, related_tests, suggestions)
        with open("report.txt", "a") as f:
            f.write(report)
if __name__ == "__main__":
    import sys
    main(repo_path=sys.argv[1], test_dir=sys.argv[2])
