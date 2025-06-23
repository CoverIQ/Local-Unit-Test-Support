import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from diff_extractor import GitDiffExtractor

@pytest.fixture
def mock_repo_path(tmp_path):
    """Create a temporary repository path for testing."""
    return str(tmp_path / "test_repo")

@pytest.fixture
def git_diff_extractor(mock_repo_path):
    """Create a GitDiffExtractor instance for testing."""
    with patch('git.Repo') as mock_repo:
        mock_repo.return_value = MagicMock()
        extractor = GitDiffExtractor(
            repo_url="https://github.com/test/repo.git",
            from_commit="HEAD^",
            to_commit="HEAD",
            keep_repo=True
        )
        extractor.repo_path = mock_repo_path
        yield extractor

def test_init_with_keep_repo(git_diff_extractor, mock_repo_path):
    """Test initialization with keep_repo=True."""
    assert git_diff_extractor.repo_path == mock_repo_path
    assert git_diff_extractor.from_commit == "HEAD^"
    assert git_diff_extractor.to_commit == "HEAD"
    assert git_diff_extractor.keep_repo is True

def test_get_changed_files(git_diff_extractor):
    """Test getting changed files."""
    mock_diff = MagicMock()
    mock_diff.a_path = "test_file.py"
    mock_diff.b_path = "test_file.py"
    mock_diff.change_type = "M"
    
    git_diff_extractor.repo.commit().diff.return_value = [mock_diff]
    
    changed_files = git_diff_extractor.get_changed_files()
    assert len(changed_files) == 1
    assert changed_files[0] == "test_file.py"

def test_load_file(git_diff_extractor, mock_repo_path):
    """Test loading file content."""
    test_file = Path(mock_repo_path) / "test_file.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("def test_func():\n    pass")
    
    content = git_diff_extractor.load_file("test_file.py")
    assert content == "def test_func():\n    pass"

def test_load_file_from_previous_commit(git_diff_extractor):
    """Test loading file from previous commit."""
    mock_blob = MagicMock()
    mock_blob.data_stream.read.return_value = b"def test_func():\n    pass"
    
    git_diff_extractor.repo.commit().tree.__getitem__.return_value = mock_blob
    
    content = git_diff_extractor.load_file_from_previous_commit("test_file.py", "HEAD^")
    assert content == "def test_func():\n    pass"

def test_get_diff(git_diff_extractor):
    """Test getting diff for a file."""
    mock_diff = MagicMock()
    mock_diff.diff.decode.return_value = "diff content"
    
    git_diff_extractor.repo.commit().diff.return_value = [mock_diff]
    
    diff = git_diff_extractor.get_diff("test_file.py")
    assert diff == "diff content"

def test_cleanup(git_diff_extractor, mock_repo_path):
    """Test cleanup of repository."""
    with patch('shutil.rmtree') as mock_rmtree:
        git_diff_extractor.cleanup()
        mock_rmtree.assert_called_once_with(mock_repo_path) 