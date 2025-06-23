# Test Maintenance Report

This report generates suggestions for updating your unit tests based on file changes. 
## Suggestion 1
#### Suggestion type: remove
#### Test function name: test_subtract
### Description
The 'subtract' function has been removed from math_utils.py, so this test for the removed function should also be removed.
### Original Code
```python
def test_subtract():
    result = subtract(10, 3)
    assert result == 7
```
### Updated Code
```python
 
```
## Suggestion 2
#### Suggestion type: remove
#### Test function name: test_subtract_negative
### Description
The 'subtract' function has been removed from math_utils.py, so this test for the removed function should also be removed.
### Original Code
```python
def test_subtract_negative():
    result = subtract(2, 3)
    assert result == -1
```
### Updated Code
```python
 
```
