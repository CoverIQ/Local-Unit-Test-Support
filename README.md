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
* How to use: check the diff_parser.main for more detail
```
python ./RegressionTest/diff_parser.py https://github.com/CoverIQ/CoverIQ-Test-Assistant
```