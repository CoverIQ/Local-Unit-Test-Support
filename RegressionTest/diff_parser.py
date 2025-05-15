import subprocess
from typing import List
import os
import tempfile
import sys
from pathlib import Path
import argparse
import shutil

def get_changed_files(repo_path: str, from_commit:str, to_commit:str) -> List[str]:
    cmd = ["git", "-C", repo_path, "diff", "--name-only", from_commit, to_commit]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(repo_path,result.stdout)
    return result.stdout.strip().split("\n")

def get_diff(repo_path: str, file_path: str, from_commit:str, to_commit:str) -> str:
    cmd = ["git", "-C", repo_path, "diff", from_commit, to_commit, "--", file_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def load_file(repo_path, file_path):
    with open(os.path.join(repo_path, file_path)) as f:
        return f.read()

def load_file_from_previous_commit(repo_path: str, file_path: str, from_commit:str) -> str:
    cmd = ["git", "-C", repo_path, "show", f"{from_commit}:{file_path}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Warning: Could not load previous version of {file_path}")
        return ""
    return result.stdout

class GitDiffParser:
    def __init__(self,repo_url, from_commit="HEAD^", to_commit="HEAD", keep_repo=False):
        self.from_commit = from_commit
        self.to_commit = to_commit
        self.keep_repo = keep_repo
        
        if keep_repo:
            temp_dir = Path("./cloned_repo")
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir, exist_ok=True)
        else:
            temp_dir = Path(tempfile.mkdtemp())

        self.temp_dir = temp_dir
        self.repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        self.repo_path = temp_dir / self.repo_name

        print(f"Cloning {repo_url} into {self.repo_path}")
        self.run_command(f"git clone {repo_url}", cwd=temp_dir)
        print(f"Fetching diff: {from_commit} -> {to_commit}")
        
        
    def run_command(self,cmd, cwd=None):
        result = subprocess.run(cmd, shell=True, text=True, capture_output=True, cwd=cwd)
        if result.returncode != 0:
            print(f"Error running command: {cmd}")
            print(result.stderr)
            sys.exit(1)
        return result.stdout
    
    def get_changed_files(self):
        return get_changed_files(self.repo_path, self.from_commit, self.to_commit)

    def load_file(self, file_path):
        return load_file(self.repo_path, file_path)
    
    def load_file_from_previous_commit(self, file_path):
        return load_file_from_previous_commit(self.repo_path, file_path, self.from_commit)
    
    def get_diff(self, file_path):
        return get_diff(self.repo_path, file_path, self.from_commit, self.to_commit)

  
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show git diff between two commits in a GitHub repo")
    parser.add_argument("repo_url", help="GitHub repository URL")
    parser.add_argument("--from", dest="from_commit", default="HEAD^", help="Base commit (default: HEAD^)")
    parser.add_argument("--to", dest="to_commit", default="HEAD", help="Target commit (default: HEAD)")
    parser.add_argument("--keep", action="store_true", help="Keep cloned repo after diff (default: delete)")

    args = parser.parse_args()
    
    dif_parser = GitDiffParser(args.repo_url, args.from_commit, args.to_commit, args.keep)
    changed_files = dif_parser.get_changed_files()
    for file in changed_files:
        print(f"Changed file: {file}")
        diff = dif_parser.get_diff(file)
        print("get different: ",diff)
