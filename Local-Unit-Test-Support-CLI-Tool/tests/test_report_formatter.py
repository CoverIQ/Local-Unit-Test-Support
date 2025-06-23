import pytest
from report_formatter import generate_suggestion_markdown

def test_generate_suggestion_markdown():
    """Test generating markdown report from suggestions."""
    suggestions = [
        {
            "suggestion_type": "add",
            "test_function_name": "test_new_feature",
            "description": "Add test for new feature",
            "original_code": "",
            "updated_code": "def test_new_feature():\n    assert True"
        },
        {
            "suggestion_type": "update",
            "test_function_name": "test_existing_feature",
            "description": "Update test for existing feature",
            "original_code": "def test_existing_feature():\n    pass",
            "updated_code": "def test_existing_feature():\n    assert True"
        }
    ]
    
    markdown = generate_suggestion_markdown(suggestions)
    
    # Check that all suggestion components are in the markdown
    assert "## test_new_feature" in markdown
    assert "## test_existing_feature" in markdown
    assert "Add test for new feature" in markdown
    assert "Update test for existing feature" in markdown
    assert "def test_new_feature()" in markdown
    assert "def test_existing_feature()" in markdown
    assert "assert True" in markdown

def test_generate_suggestion_markdown_empty():
    """Test generating markdown report with empty suggestions."""
    suggestions = []
    markdown = generate_suggestion_markdown(suggestions)
    assert "No suggestions available" in markdown

def test_generate_suggestion_markdown_single():
    """Test generating markdown report with single suggestion."""
    suggestions = [
        {
            "suggestion_type": "add",
            "test_function_name": "test_single",
            "description": "Single test suggestion",
            "original_code": "",
            "updated_code": "def test_single():\n    assert True"
        }
    ]
    
    markdown = generate_suggestion_markdown(suggestions)
    
    assert "## test_single" in markdown
    assert "Single test suggestion" in markdown
    assert "def test_single()" in markdown
    assert "assert True" in markdown

def test_generate_suggestion_markdown_with_code_blocks():
    """Test generating markdown report with code blocks."""
    suggestions = [
        {
            "suggestion_type": "update",
            "test_function_name": "test_complex",
            "description": "Update complex test",
            "original_code": """def test_complex():
    result = complex_function()
    assert result == expected""",
            "updated_code": """def test_complex():
    result = complex_function()
    assert result == expected
    assert result.is_valid()"""
        }
    ]
    
    markdown = generate_suggestion_markdown(suggestions)
    
    assert "## test_complex" in markdown
    assert "Update complex test" in markdown
    assert "```python" in markdown
    assert "def test_complex():" in markdown
    assert "assert result.is_valid()" in markdown 