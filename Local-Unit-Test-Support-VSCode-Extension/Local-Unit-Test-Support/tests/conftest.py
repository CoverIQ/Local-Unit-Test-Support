import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

@pytest.fixture(scope="session")
def test_dir(tmp_path_factory):
    """Create a temporary directory for all tests."""
    return tmp_path_factory.mktemp("test_dir")

@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        "GOOGLE_API_KEY": "test_api_key"
    }):
        yield

@pytest.fixture
def mock_gemini_model():
    """Mock Gemini model for testing."""
    with patch('genai.GenerativeModel') as mock_model:
        mock_model.return_value.embed_content.return_value.embedding = [0.1] * 768
        mock_model.return_value.generate_content.return_value.text = "test response"
        yield mock_model

@pytest.fixture
def sample_code_blocks():
    """Create sample code blocks for testing."""
    return {
        ("test_file.py", "func1"): {
            "symbol_type": "function",
            "symbol_name": "func1",
            "file_path": "test_file.py",
            "code": "def func1():\n    pass"
        },
        ("test_file.py", "func2"): {
            "symbol_type": "function",
            "symbol_name": "func2",
            "file_path": "test_file.py",
            "code": "def func2():\n    return True"
        }
    }

@pytest.fixture
def sample_test_code():
    """Create sample test code for testing."""
    return """
def test_func1():
    result = func1()
    assert result is None

def test_func2():
    result = func2()
    assert result is True
    """

@pytest.fixture
def sample_git_diff():
    """Create sample git diff for testing."""
    return """
diff --git a/test_file.py b/test_file.py
index abc123..def456 100644
--- a/test_file.py
+++ b/test_file.py
@@ -1,3 +1,4 @@
 def func1():
-    pass
+    return None
"""

@pytest.fixture
def mock_repo():
    """Create a mock git repository for testing."""
    with patch('git.Repo') as mock_repo:
        mock_repo.return_value = MagicMock()
        mock_repo.return_value.commit.return_value.diff.return_value = [
            MagicMock(
                a_path="test_file.py",
                b_path="test_file.py",
                change_type="M",
                diff=b"diff content"
            )
        ]
        yield mock_repo 