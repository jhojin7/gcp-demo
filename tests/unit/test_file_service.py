import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from services.file_service import FileService
from models.user import User
from models.file import File
from models.file_version import FileVersion

@pytest.fixture
def mock_gcp_service():
    """Fixture to mock the GCPStorageService."""
    return MagicMock()

@pytest.fixture
def file_service(mock_gcp_service):
    """Fixture to create a FileService with a mocked GCP service."""
    return FileService(mock_gcp_service)

@pytest.fixture
def test_user():
    """Fixture for a test user."""
    return User(user_id="user1", display_name="Test User")

@patch('magic.from_buffer', return_value='text/plain')
def test_upload_new_file(mock_magic, file_service, mock_gcp_service, test_user):
    """Test uploading a new file."""
    file_content = b"test"
    filename = "test.txt"
    virtual_path = "/"
    
    mock_gcp_service.upload_file.return_value = FileVersion(
        version_id="1",
        file_storage_key="user1/files/test.txt",
        size_bytes=4,
        created_at=datetime.now(timezone.utc),
        created_by=test_user.user_id,
        operation_type="upload"
    )
    mock_gcp_service.list_files.return_value = []

    file, version, operation = file_service.upload_file(
        file_content, filename, virtual_path, test_user
    )

    mock_gcp_service.upload_file.assert_called_once()
    assert file.display_name == filename
    assert version.operation_type == "upload"

@patch('magic.from_buffer', return_value='text/plain')
def test_upload_new_version(mock_magic, file_service, mock_gcp_service, test_user):
    """Test uploading a new version of an existing file."""
    file_content = b"new content"
    filename = "test.txt"
    virtual_path = "/"
    
    existing_file = File(
        display_name=filename,
        storage_key="user1/files/test.txt",
        content_type="text/plain",
        virtual_path=virtual_path,
        owner_id=test_user.user_id
    )
    mock_gcp_service.list_files.return_value = [existing_file]
    mock_gcp_service.upload_file.return_value = FileVersion(
        version_id="2",
        file_storage_key="user1/files/test.txt",
        size_bytes=11,
        created_at=datetime.now(timezone.utc),
        created_by=test_user.user_id,
        operation_type="edit"
    )

    file, version, operation = file_service.upload_file(
        file_content, filename, virtual_path, test_user
    )

    mock_gcp_service.upload_file.assert_called_once()
    assert version.operation_type == "edit"

def test_download_file(file_service, mock_gcp_service, test_user):
    """Test downloading a file."""
    file_id = "user1/files/test.txt"
    file_obj = File(
        display_name="test.txt",
        storage_key=file_id,
        content_type="text/plain",
        virtual_path="/",
        owner_id=test_user.user_id
    )
    mock_gcp_service.file_exists.return_value = True
    mock_gcp_service.get_file_info.return_value = {'metadata': {'owner_id': test_user.user_id}}
    mock_gcp_service.download_file.return_value = (b"content", {})
    
    with patch.object(file_service, '_get_file_by_id_or_path', return_value=file_obj):
        content, filename, operation = file_service.download_file(file_id, test_user)

    assert content == b"content"
    assert filename == "test.txt"

def test_delete_file(file_service, mock_gcp_service, test_user):
    """Test deleting a file."""
    file_id = "user1/files/test.txt"
    file_obj = File(
        display_name="test.txt",
        storage_key=file_id,
        content_type="text/plain",
        virtual_path="/",
        owner_id=test_user.user_id
    )
    with patch.object(file_service, '_get_file_by_id_or_path', return_value=file_obj):
        operation = file_service.delete_file(file_id, test_user)

    mock_gcp_service.delete_file.assert_called_once_with(file_id)
    assert file_obj.is_deleted

def test_normalize_virtual_path(file_service):
    """Test virtual path normalization and traversal prevention."""
    assert file_service._normalize_virtual_path("docs/reports") == "/docs/reports/"
    assert file_service._normalize_virtual_path("/a/b/../c/") == "/a/c/"
    assert file_service._normalize_virtual_path("/a/../../b/") == "/b/"
    assert file_service._normalize_virtual_path("/") == "/"
    assert file_service._normalize_virtual_path("") == "/"