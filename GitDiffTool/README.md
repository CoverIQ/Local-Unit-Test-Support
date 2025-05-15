# Git Diff Tool

A simple Python script to show the `git diff` between two commits of a GitHub repository.

## Requirements

- Python 3.6+
- Git installed

## Usage

```bash
python git_diff.py <repo_url> [--from COMMIT] [--to COMMIT] [--keep] [--output FILE]
```

### Options

- `--from`: Base commit (default: `HEAD^`)
- `--to`: Target commit (default: `HEAD`)
- `--keep`: Keep the cloned repo (default: repo is deleted after diff)
- `--output`: Save diff to a file

### Examples

```bash
python git_diff.py https://github.com/user/repo.git

python git_diff.py https://github.com/user/repo.git --from abc123 --to def456

python git_diff.py https://github.com/user/repo.git --output diff.txt --keep
```
