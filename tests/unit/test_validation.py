import pytest
from unittest.mock import patch, MagicMock
from services.file_service import FileService

@pytest.fixture
def file_service():
    return FileService(gcp_service=MagicMock())

@patch('magic.from_buffer')
@patch('config.Config.is_file_allowed')
def test_validate_file_content_allowed(mock_is_file_allowed, mock_from_buffer, file_service):
    """Test that file content validation passes for allowed files."""
    mock_from_buffer.return_value = 'text/plain'
    mock_is_file_allowed.return_value = True
    
    file_service._validate_file_content(b"test content", "test.txt")
    
    mock_is_file_allowed.assert_called_once_with("test.txt", 'text/plain')

@patch('magic.from_buffer')
@patch('config.Config.is_file_allowed')
def test_validate_file_content_not_allowed(mock_is_file_allowed, mock_from_buffer, file_service):
    """Test that file content validation fails for disallowed files."""
    mock_from_buffer.return_value = 'application/x-msdownload'
    mock_is_file_allowed.return_value = False
    
    with pytest.raises(ValueError, match="File type not allowed"):
        file_service._validate_file_content(b"test content", "test.exe")

def test_empty_file_validation(file_service):
    """Test that empty files are not allowed."""
    with pytest.raises(ValueError, match="Empty file cannot be uploaded"):
        file_service._validate_file_content(b"", "empty.txt")
