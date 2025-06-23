import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from main import (
    load_existing_index,
    process_code_files,
    analyze_changed_files,
    process_test_files,
    generate_report,
    main
)

@pytest.fixture
def mock_repo_path(tmp_path):
    """Create a temporary repository path for testing."""
    return str(tmp_path / "test_repo")

@pytest.fixture
def mock_git_diff_extractor():
    """Create a mock GitDiffExtractor instance."""
    with patch('diff_extractor.GitDiffExtractor') as mock_extractor:
        mock_extractor.return_value.repo_path = "test_repo"
        mock_extractor.return_value.from_commit = "HEAD^"
        mock_extractor.return_value.to_commit = "HEAD"
        yield mock_extractor

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

def test_load_existing_index(tmp_path):
    """Test loading existing index and metadata."""
    index_path = tmp_path / "index.faiss"
    meta_path = tmp_path / "metadata.json"
    
    # Create mock metadata
    import json
    metadata = [
        {
            "symbol_type": "function",
            "symbol_name": "func1",
            "file_path": "test_file.py",
            "code": "def func1():\n    pass"
        }
    ]
    with open(meta_path, 'w') as f:
        json.dump(metadata, f)
    
    # Create empty FAISS index
    import faiss
    index = faiss.IndexFlatL2(768)
    faiss.write_index(index, str(index_path))
    
    code_blocks, exists = load_existing_index(str(index_path), str(meta_path))
    assert exists
    assert len(code_blocks) == 1
    assert ("test_file.py", "func1") in code_blocks

def test_process_code_files(mock_repo_path, mock_code_blocks):
    """Test processing code files."""
    with patch('main.load_existing_index') as mock_load:
        mock_load.return_value = (mock_code_blocks, True)
        code_blocks = process_code_files(mock_repo_path)
        assert code_blocks == mock_code_blocks

def test_analyze_changed_files(mock_git_diff_extractor):
    """Test analyzing changed files."""
    mock_diff = MagicMock()
    mock_diff.a_path = "test_file.py"
    mock_diff.b_path = "test_file.py"
    mock_diff.change_type = "M"
    
    mock_git_diff_extractor.return_value.get_changed_files.return_value = ["test_file.py"]
    mock_git_diff_extractor.return_value.load_file_from_previous_commit.return_value = "def func1():\n    pass"
    mock_git_diff_extractor.return_value.get_diff.return_value = "diff content"
    
    changed_functions, all_changed, whole_git_diff = analyze_changed_files(mock_git_diff_extractor.return_value)
    assert len(changed_functions) > 0
    assert len(all_changed) > 0
    assert whole_git_diff == "diff content"

def test_process_test_files(mock_repo_path, mock_code_blocks):
    """Test processing test files."""
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            (mock_repo_path, [], ["test_file.py"])
        ]
        
        with patch('builtins.open', MagicMock()) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = """
def test_func1():
    func1()
    assert True
            """
            
            affected_metadata, whole_test_code = process_test_files(
                mock_repo_path,
                ["func1"],
                mock_code_blocks
            )
            
            assert len(affected_metadata) > 0
            assert "test_func1" in whole_test_code

def test_generate_report(tmp_path):
    """Test generating report."""
    output_filename = str(tmp_path / "test_report.md")
    
    with patch('rag_generation.GeminiSuggester') as mock_suggester:
        mock_suggester.return_value.get_test_suggestions.return_value = [
            {
                "suggestion_type": "add",
                "test_function_name": "test_new",
                "description": "Add new test",
                "original_code": "",
                "updated_code": "def test_new():\n    assert True"
            }
        ]
        
        generate_report(
            affected_metadata_list=[{"symbol_name": "test_func"}],
            whole_test_code="def test_func():\n    pass",
            whole_git_diff="diff content",
            output_filename=output_filename
        )
        
        assert os.path.exists(output_filename)
        with open(output_filename, 'r') as f:
            content = f.read()
            assert "Test Maintenance Report" in content
            assert "test_new" in content

def test_main_workflow(mock_repo_path, mock_git_diff_extractor, mock_code_blocks):
    """Test the complete main workflow."""
    with patch('main.load_existing_index') as mock_load:
        mock_load.return_value = (mock_code_blocks, True)
        
        with patch('main.analyze_changed_files') as mock_analyze:
            mock_analyze.return_value = (
                {"test_file.py": {"modified": ["func1"]}},
                ["func1"],
                "diff content"
            )
            
            with patch('main.process_test_files') as mock_process:
                mock_process.return_value = (
                    [{"symbol_name": "test_func"}],
                    "def test_func():\n    pass"
                )
                
                with patch('main.generate_report') as mock_report:
                    main(
                        repo_url="https://github.com/test/repo.git",
                        from_commit="HEAD^",
                        to_commit="HEAD",
                        keep_repo=True,
                        output_filename="test_report"
                    )
                    
                    mock_report.assert_called_once() 