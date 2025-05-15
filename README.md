# Regression Testing Roport Tool
## Module lists
- diff_parser
    - According to the git link output the relative code changing   
- ast_analyzer
    - Deal with raw data which is the output of diff_parser, make it readable. 
- test_linker
    - Find the relative testing api
- llm_engine
    - use llm to give the user suggestion
- reporter
    - output a human frendily report

## diff_parser.GitDiffParser
### API
* init: clone the target repo
* get_changed_files: list the files which have been changed
* load_file: return the source code of the target commit
* load_file_from_previous_commit: return the source code of the base commit
* get_diff: return the git diff result between target and base commit
#### Easy way to call api
1. Inital the class with correct parameters
2. use get_changed_files to get the name list of modified files
3. load_file and load_file_from_previous_commit to load the specific function in the output of get_changed_files
4. use the both output of load_file and load_file_from_previous_commit as an input of ast_analyzer to analyze different
### Usage
```bash
python ./RegressionTest/diff_parser.py <repo_url> [--from COMMIT] [--to COMMIT] [--keep] 
```

#### Options

- `--from`: Base commit (default: `HEAD^`)
- `--to`: Target commit (default: `HEAD`)
- `--keep`: Keep the cloned repo (default: repo is deleted after diff)

#### Examples

```bash
python ./RegressionTest/diff_parser.py https://github.com/CoverIQ/CoverIQ-Test-Assistant

python ./RegressionTest/diff_parser.py https://github.com/CoverIQ/CoverIQ-Test-Assistant --from abc123 --to def456

python ./RegressionTest/diff_parser.py https://github.com/CoverIQ/CoverIQ-Test-Assistant --keep
```
