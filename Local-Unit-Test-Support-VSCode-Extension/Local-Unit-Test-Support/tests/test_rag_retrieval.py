import os
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock
from rag_retrieval import get_embedding, save_to_faiss, get_code_files

@pytest.fixture
def mock_embedding():
    """Create a mock embedding for testing."""
    return np.random.rand(768).astype(np.float32)

@pytest.fixture
def mock_code_blocks():
    """Create mock code blocks for testing."""
    return {
        ("test_file.py", "func1"): {
            "symbol_type": "function",
            "symbol_name": "func1",
            "file_path": "test_file.py",
            "code": "def func1():\n    pass"
        }
    }

def test_get_embedding():
    """Test getting embedding from Gemini API."""
    with patch('genai.GenerativeModel') as mock_model:
        mock_model.return_value.embed_content.return_value.embedding = [0.1] * 768
        embedding = get_embedding("test text")
        assert len(embedding) == 768
        assert all(isinstance(x, float) for x in embedding)

def test_get_embedding_error():
    """Test error handling in get_embedding."""
    with patch('genai.GenerativeModel') as mock_model:
        mock_model.return_value.embed_content.side_effect = Exception("API Error")
        with pytest.raises(Exception) as exc_info:
            get_embedding("test text")
        assert "API Error" in str(exc_info.value)

def test_save_to_faiss(tmp_path, mock_embedding, mock_code_blocks):
    """Test saving embeddings to FAISS index."""
    index_path = tmp_path / "test_index.faiss"
    meta_path = tmp_path / "test_metadata.json"
    
    embeddings = [mock_embedding]
    save_to_faiss(embeddings, mock_code_blocks, str(index_path), str(meta_path))
    
    assert index_path.exists()
    assert meta_path.exists()
    
    # Verify metadata content
    import json
    with open(meta_path, 'r') as f:
        metadata = json.load(f)
    assert len(metadata) == 1
    assert metadata[0]["symbol_name"] == "func1"

def test_save_to_faiss_empty_embeddings(tmp_path, mock_code_blocks):
    """Test saving empty embeddings to FAISS index."""
    index_path = tmp_path / "test_index.faiss"
    meta_path = tmp_path / "test_metadata.json"
    
    with pytest.raises(ValueError) as exc_info:
        save_to_faiss([], mock_code_blocks, str(index_path), str(meta_path))
    assert "No embeddings provided" in str(exc_info.value)

def test_get_code_files(tmp_path):
    """Test getting code files from repository."""
    # Create test directory structure
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    
    # Create Python files
    (repo_path / "test_file.py").write_text("def test():\n    pass")
    (repo_path / "test_file2.py").write_text("def test2():\n    pass")
    
    # Create excluded directories
    (repo_path / "venv").mkdir()
    (repo_path / "__pycache__").mkdir()
    (repo_path / "venv" / "test_file.py").write_text("def test():\n    pass")
    
    files = get_code_files(str(repo_path))
    assert len(files) == 2
    assert all(str(f).endswith(".py") for f in files)
    assert not any("venv" in str(f) for f in files)
    assert not any("__pycache__" in str(f) for f in files)

def test_get_code_files_with_custom_pattern(tmp_path):
    """Test getting code files with custom pattern."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    
    # Create test files
    (repo_path / "test_file.py").write_text("def test():\n    pass")
    (repo_path / "test_file.txt").write_text("test content")
    
    files = get_code_files(str(repo_path), include_pattern="*.txt")
    assert len(files) == 1
    assert str(files[0]).endswith(".txt") 