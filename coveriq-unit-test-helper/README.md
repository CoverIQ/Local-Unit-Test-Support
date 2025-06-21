## Contents
- [Introduction](#introduction)
- [Examples](#add-test-example)
    -  [Adding test cases](#add-test-example)
    -  [Removing test cases](#remove-test-example)
    -  [Updating test cases](#update-test-example)
- [System Workflow](#system-workflow)
- [Installation](#installation)
- [Usage](#usage)


## Introduction

**CoverIQ Unit Test Helper** extension intelligently analyzes your project's Git history to understand recent code changes. It then provides clear, actionable suggestions to `add`, `update`, or `remove` tests, ensuring your test suite remains relevant and robust. All suggestions are presented in a clean Markdown report, right inside your IDE, for you to review and act upon.

The goal is to help you maintain high-quality test coverage with minimal effort, allowing you to focus more on development.

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

## System Workflow
### User Interaction in VS Code
- Launch analysis via Command Palette or editor icon
- Select commit range from an interactive Git log dropdown
### Extension Core (TypeScript)
- Gathers context (selected commits, workspace path)
- Executes the backend Python engine with the captured context
### Python Analysis Engine
- Analyzes code changes using AST parsing and RAG (with Gemini)
- Generates a structured list of test maintenance suggestions
### Markdown Report Viewer
- Saves the analysis results as a `report.md` file in the workspace


## Installation
### Python
Python 3.9+  
Node.js 18+

### Add .env
* Add .env under `Local-Unit-Test-Support` folder
* Edit .env file and add GEMINI_API_KEY into it
```
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

### Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Install Node.js dependencies
```bash
npm install
```

### Set Python executable path from virtual environment
* Go to `package.json` file
* Go to `contributes` &rightarrow; `configuration` &rightarrow; `properties` &rightarrow; `coveriq.pythonPath` &rightarrow;
* Set the path to `default`


### VS Code Version
* Make sure your VS Code Version is over 1.101.0

### Usage
* Go to `/src/extension.ts`
* Press F5
* Pick the work directory you want to anaylze
* Clone the [example repo](https://github.com/HankStat/CoverIQ-Unit-Test-Support-Demo) and choose the root directory as work directory
* Press Ctrl+Shift+P and type **Analyze Unit Tests with CoverIQ** or click the **Analyze Unit Tests with CoverIQ** button on the upper right corner
* Pick the base commit
![Pick FROM commit](https://github.com/user-attachments/assets/a5182413-b2c3-4b0d-bca6-d883c56ba78a)
* Pick the target commit
![Pick TO commit](https://github.com/user-attachments/assets/1a7de01f-92a2-4cfb-a815-1736a449e035)
* It will show the preview result in the work directory
