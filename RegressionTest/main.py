import os
import sys
from pathlib import Path
import argparse

from diff_parser import GitDiffParser
from ast_analyzer import analyze_ast_diff
from test_linker import extract_called_functions_from_test
from llm_engine import suggest_test_changes
from reporter import generate_markdown_report

def main(repo_url, from_commit, to_commit, keep_repo):
    git_parser = GitDiffParser(repo_url, from_commit, to_commit, keep_repo)
    repo_path = git_parser.repo_path

    # Clear previous report
    with open("report.md", "w") as f:
        f.write("# Test Maintenance Report\n\n")

    # Step 1: Get changed files and functions
    changed_files = git_parser.get_changed_files()
    changed_functions = {}

    for file in changed_files:
        if not file.endswith(".py"):
            continue

        before_code = git_parser.load_file_from_previous_commit(file)
        after_code = git_parser.load_file(file)
        changes = analyze_ast_diff(before_code, after_code)
        changed_functions[file] = changes

    # Step 2: Walk through test files and match them to changed functions
    for root, _, files in os.walk(repo_path):
        for filename in files:
            if "test" in filename and filename.endswith(".py"):
                # print(f"Processing test file: {filename}")
                test_path = os.path.join(root, filename)
                with open(test_path, "r") as tf:
                    try:
                        test_code = tf.read()
                        called_funcs = extract_called_functions_from_test(test_code)
                    except Exception as e:
                        print(f"Error parsing {test_path}: {e}")
                        continue

                # Match called functions to changed ones
                matched_funcs = {}
                for file, changes in changed_functions.items():
                    all_changed = (
                        changes.get("added", []) +
                        changes.get("removed", []) +
                        changes.get("modified", []) +
                        changes.get("indirect_dependents", [])
                    )
                    match = list(set(called_funcs).intersection(all_changed))
                    if match:
                        matched_funcs[file] = match

                # Flatten the matches to build suggestions
                for file, funcs in matched_funcs.items():
                    after_code = git_parser.load_file(file)
                    suggestions = {
                        func: suggest_test_changes(func, after_code)
                        for func in funcs
                    }

                    report = generate_markdown_report(
                        test_path,
                        changed_functions[file],
                        {func: [test_path] for func in funcs},
                        suggestions
                    )
                    with open("report.md", "a") as f:
                        f.write(report)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show git diff between two commits in a GitHub repo")
    parser.add_argument("repo_url", help="GitHub repository URL")
    parser.add_argument("--from", dest="from_commit", default="HEAD^", help="Base commit (default: HEAD^)")
    parser.add_argument("--to", dest="to_commit", default="HEAD", help="Target commit (default: HEAD)")
    parser.add_argument("--keep",  action="store_true", help="Keep cloned repo after diff (default: delete)")

    args = parser.parse_args()
    
    main(args.repo_url, args.from_commit, args.to_commit, args.keep)
