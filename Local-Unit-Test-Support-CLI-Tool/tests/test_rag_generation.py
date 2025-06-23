import pytest
from unittest.mock import patch, MagicMock
from rag_generation import GeminiSuggester, SuggestionSchema, SuggestionResponse

@pytest.fixture
def mock_suggestions():
    """Create mock suggestions for testing."""
    return [
        {
            "suggestion_type": "add",
            "test_function_name": "test_new_feature",
            "description": "Add test for new feature",
            "original_code": "",
            "updated_code": "def test_new_feature():\n    assert True"
        }
    ]

@pytest.fixture
def mock_affected_metadata():
    """Create mock affected metadata for testing."""
    return [
        {
            "symbol_type": "function",
            "symbol_name": "test_func",
            "file_path": "test_file.py",
            "code": "def test_func():\n    pass"
        }
    ]

def test_gemini_suggester_init():
    """Test GeminiSuggester initialization."""
    with patch('genai.GenerativeModel') as mock_model:
        suggester = GeminiSuggester()
        assert suggester.model is not None

def test_get_coverage_suggestions(mock_suggestions):
    """Test getting coverage suggestions."""
    with patch('genai.GenerativeModel') as mock_model:
        mock_model.return_value.generate_content.return_value.text = str(mock_suggestions)
        suggester = GeminiSuggester()
        
        suggestions = suggester.get_coverage_suggestions(
            function_name=["test_func"],
            code="def test_func():\n    pass",
            git_diff_message="diff content"
        )
        
        assert len(suggestions) == 1
        assert suggestions[0]["suggestion_type"] == "add"
        assert suggestions[0]["test_function_name"] == "test_new_feature"

def test_get_test_suggestions(mock_suggestions, mock_affected_metadata):
    """Test getting test suggestions."""
    with patch('genai.GenerativeModel') as mock_model:
        mock_model.return_value.generate_content.return_value.text = str(mock_suggestions)
        suggester = GeminiSuggester()
        
        suggestions = suggester.get_test_suggestions(
            affected_metadata_list=mock_affected_metadata,
            whole_test_code="def test_func():\n    pass",
            git_diff_message="diff content"
        )
        
        assert len(suggestions) == 1
        assert suggestions[0]["suggestion_type"] == "add"
        assert suggestions[0]["test_function_name"] == "test_new_feature"

def test_suggestion_schema():
    """Test SuggestionSchema validation."""
    suggestion = SuggestionSchema(
        suggestion_type="add",
        test_function_name="test_func",
        description="Test description",
        original_code="def test_func():\n    pass",
        updated_code="def test_func():\n    assert True"
    )
    
    assert suggestion.suggestion_type == "add"
    assert suggestion.test_function_name == "test_func"
    assert suggestion.description == "Test description"
    assert "def test_func()" in suggestion.original_code
    assert "assert True" in suggestion.updated_code

def test_suggestion_response():
    """Test SuggestionResponse validation."""
    suggestions = [
        SuggestionSchema(
            suggestion_type="add",
            test_function_name="test_func",
            description="Test description",
            original_code="def test_func():\n    pass",
            updated_code="def test_func():\n    assert True"
        )
    ]
    
    response = SuggestionResponse(suggestions=suggestions)
    assert len(response.suggestions) == 1
    assert response.suggestions[0].suggestion_type == "add"
    assert response.suggestions[0].test_function_name == "test_func" 