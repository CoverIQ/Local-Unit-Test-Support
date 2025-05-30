# Local Unit Test Support
### An AI-Powered `Local Unit Test Maintenance Solution` provided by `CoverIQ`. 
## Contents
- [Introduction](#introduction)
- [Examples](#add-test-example)
    -  [Adding test cases](#add-test-example)
    -  [Removing test cases](#remove-test-example)
    -  [Updating test cases](#update-test-example)
- [System Workflow](#system-workflow)
- [Installation](#installation)
- [Example Execution Commands](#example-execution-commands)
## Introduction
This tool leverages RAG to analyze git diffs, affected test functions, and test code, providing suggestions in a report with the following format: 
- suggestion type
- test function name
- description
- original code
- updated code

We use [example repo](https://github.com/HankStat/CoverIQ-Unit-Test-Support-Demo.git) to showcase how the tool works in practice. 

## `Add` Test Example
<!-- [Commit Change Link](https://github.com/HankStat/CoverIQ-Unit-Test-Support-Demo/commit/150831357ecca2d2ed946bf36ed4a85131276e77) -->
### Commit Change
Add `multiply` function in `math_utils.py`  
However, No corresponding test function was added for the newly added function  
```python
def multiply(x, y):
    return x * y
```   
### Suggestion
- ### Description  
Add test cases for the new 'multiply' function in math_utils.py.
- ### Suggested Code Addition  
```python
from math_utils import add, subtract, pad_number, multiply
def test_multiply():
    result = multiply(2, 3)
    assert result == 6
    result = multiply(-2, 3)
    assert result == -6
    result = multiply(0, 5)
    assert result == 0
    result = multiply(-4, -5)
    assert result == 20
    result = multiply(2.5, 4)
    assert result == 10.0
```  
[Full Report](/Local-Unit-Test-Support/ExampleReports/add_report.md)

## `Remove` Test Example
<!-- [Commit Change Link](https://github.com/HankStat/CoverIQ-Unit-Test-Support-Demo/commit/29445144fe589cb3a6086674a211f50db1579494) -->
### Commit Change
Remove `subtract` function in `math_utils.py`  
```python
def subtract(x, y):
    return x - y
```
There are two functions in `test/test_math_utils.py` that call the `subtract` function
```python
def test_subtract():
    result = subtract(10, 3)
    assert result == 7

def test_subtract_negative():
    result = subtract(2, 3)
    assert result == -1
```
### Suggestion
The LLM gives two suggestions: one to remove `test_subtract`, and another to remove `test_subtract_negative`  
<!-- Below is the first suggestion to remove `test_subtract`       
- ### Description  
The 'subtract' function has been removed from math_utils.py, so this (`test_subtract`) test for the removed function should also be removed.
- ### Suggested Code Removal 
```python
def test_subtract():
    result = subtract(10, 3)
    assert result == 7
```   -->
See more in the [Full Report](/Local-Unit-Test-Support/ExampleReports/remove_report.md).

## `Update` Test Example
<!-- [Commit Change Link](https://github.com/HankStat/CoverIQ-Unit-Test-Support-Demo/commit/cdebf828370103a7614175b07d0e83e8ed649ace) -->
### Commit Change
Changed the padding length in `pad_number` function in `math_utils.py` from 3 to 5   
#### Original Code
```python
def pad_number(x):
    return str(x).zfill(3)
```
#### Updated Code
```python
def pad_number(x):
    return str(x).zfill(5)
```
### Suggestion
The LLM suggests that `test_pad_num` should be modified to reflect the change, padding to a length of 5 instead of 3.       
<!-- - ### Description  
Update assertions to reflect the change in `pad_number` which now pads to a length of 5 instead of 3.
- ### Original Code
```python
def test_pad_num():
    result = pad_number(5)
    assert result == '005'
    
    result = pad_number(123)
    assert result == '123'
    
    result = pad_number(0)
    assert result == '000'
```
- ### Suggested Code 
```python
 def test_pad_num():
    result = pad_number(5)
    assert result == '00005'
    
    result = pad_number(123)
    assert result == '00123'
    
    result = pad_number(0)
    assert result == '00000'
```   -->
See more in the [Full Report](/Local-Unit-Test-Support//ExampleReports/update_report.md). 

## System Workflow
### 1. Get Code Chunks
- Retrieve all relevant code files 
- Parse each file into code chunks with metadata:
  - `symbol_type` (e.g., function, class)
  - `symbol_name`
  - `file_path`
  - `code`

### 2. Generate Embeddings
- Use the Gemini embedding model to generate embeddings for each code chunk
- Store the embeddings in a FAISS index for similarity search

### 3. Git Diff Parser
- Clone the target repository
- Compare file versions between the specified Git commits
- Extract and output code diffs for each changed file

### 4. Find Affected Test Functions
- Parse all test files.
- Construct call graphs to trace relationships
- Identify test functions affected by code changes, either directly or indirectly

### 5. Generate Suggestions
- **Input**:
  - Git diffs of changed files
  - Metadata of affected test functions
  - All test code
- **Model**: Gemini 2.5
- **Output Schema** (list of suggestions):
  - `suggestion_type`
  - `test_function_name`
  - `description`
  - `original_code`
  - `updated_code`

### 6. Export Report
- Format and export all suggestions and metadata into a readable Markdown report

## Installation
### Python
Python 3.9+
### Add .env
* Add .env under `Local-Unit-Test-Support` folder
* Edit .env file and add GEMINI_API_KEY into it
```
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

### Install Dependencies
```bash
pip install -r requirements.txt
```
### Usage
```bash
python Local-Unit-Test-Support/get_report.py <repo_url> [--from commit] [--to commit] [--keep] [--output your_output_file_name]
```

#### Options

- `--from`: Base commit (default: `HEAD^`)
- `--to`: Target commit (default: `HEAD`)
- `--keep`: Keep the cloned repo (default: repo is deleted after diff)
- `--output`: Output File Name (default: `report`)

### Example Execution Commands
#### `Add` Test Example
```bash
python Local-Unit-Test-Support/get_report.py https://github.com/HankStat/CoverIQ-Unit-Test-Support-Demo.git --from=fe80de68f76600d43d1ddc3711ade55a64b03d0b --to=150831357ecca2d2ed946bf36ed4a85131276e77 --output=add_report
```

#### `Remove` Test Example
```bash
python Local-Unit-Test-Support/get_report.py https://github.com/HankStat/CoverIQ-Unit-Test-Support-Demo.git --output=remove_report
```

#### `Update` Test Example
```bash
python Local-Unit-Test-Support/get_report.py https://github.com/HankStat/CoverIQ-Unit-Test-Support-Demo.git --from=e4f8319c380af60f2e1607cfc2afbf3dd6ecdc63 --to=3bd666a1214fe5eea1e41e87ea59bf34d5548b17 --output=update_report
```
