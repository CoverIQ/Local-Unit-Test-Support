import os
import sys
from pathlib import Path
import argparse

from diff_parser import GitDiffParser
from ast_analyzer import analyze_ast_diff
from test_linker import guess_related_tests
from llm_engine import suggest_test_changes
from reporter import generate_markdown_report

def main(repo_url, from_commit, to_commit, keep_repo, output_path):
    dif_parser = GitDiffParser(repo_url, from_commit, to_commit, keep_repo, output_path)
    test_dir=dif_parser.repo_path
    changed_files = dif_parser.get_changed_files()
    for file in changed_files:
        if not file.endswith(".py"):
            continue
        
        print("current file: ", file)
        before_code = dif_parser.load_file_from_previous_commit(file)
        after_code = dif_parser.load_file(file)
        # print(after_code)
        changes = analyze_ast_diff(before_code, after_code)
        print(changes)
        # Added functions
        related_tests = guess_related_tests(changes["added"], test_dir)
        
        suggestions = {
            func: suggest_test_changes(func, after_code)
            for func in changes["added"]
        }
        
        report = generate_markdown_report(file,changes, related_tests, suggestions)
        with open("report.txt", "a") as f:
            f.write(report)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show git diff between two commits in a GitHub repo")
    parser.add_argument("repo_url", help="GitHub repository URL")
    parser.add_argument("--from", dest="from_commit", default="HEAD^", help="Base commit (default: HEAD^)")
    parser.add_argument("--to", dest="to_commit", default="HEAD", help="Target commit (default: HEAD)")
    parser.add_argument("--keep", action="store_true", help="Keep cloned repo after diff (default: delete)")
    parser.add_argument("--output", help="File path to save diff output (optional)")

    args = parser.parse_args()
    
    main(args.repo_url, args.from_commit, args.to_commit, args.keep, args.output)
