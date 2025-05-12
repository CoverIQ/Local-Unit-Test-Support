import subprocess
from typing import List

def get_changed_files(repo_path: str) -> List[str]:
    cmd = ["git", "-C", repo_path, "diff", "--name-only", "HEAD~1", "HEAD"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    return result.stdout.strip().split("\n")

def get_diff(repo_path: str, file_path: str) -> str:
    cmd = ["git", "-C", repo_path, "diff", "HEAD~1", "HEAD", "--", file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout


if __name__ == "__main__":
    import sys
    repo_path = sys.argv[1]
    changed_files = get_changed_files(repo_path)
    for file in changed_files:
        print(f"Changed file: {file}")
        diff = get_diff(repo_path, file)
        print("\n get different: ",diff)