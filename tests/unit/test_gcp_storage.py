import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from gcp_storage import GCPStorageService
from models.file import File
from google.cloud.exceptions import NotFound, Forbidden

@pytest.fixture
def mock_storage_client(mocker):
    """Fixture to mock the GCP Storage client."""
    mock_client = MagicMock()
    mock_bucket = MagicMock()
    mock_blob = MagicMock()

    mocker.patch('google.cloud.storage.Client', return_value=mock_client)
    mock_client.bucket.return_value = mock_bucket
    mock_bucket.blob.return_value = mock_blob
    mock_bucket.versioning_enabled = True
    mock_blob.exists.return_value = True

    return mock_client, mock_bucket, mock_blob

def test_gcp_service_initialization(mock_storage_client):
    """Test GCPStorageService initialization."""
    mock_client, mock_bucket, _ = mock_storage_client
    service = GCPStorageService(project_id="test-project", bucket_name="test-bucket")
    
    mock_client.bucket.assert_called_once_with("test-bucket")
    mock_bucket.reload.assert_called_once()
    assert service._client == mock_client
    assert service._bucket == mock_bucket

def test_upload_file(mock_storage_client):
    """Test file upload."""
    _, mock_bucket, mock_blob = mock_storage_client
    service = GCPStorageService(project_id="test-project", bucket_name="test-bucket")
    
    file_content = b"test content"
    file_model = File(
        display_name="test.txt",
        storage_key="user1/files/test.txt",
        content_type="text/plain",
        virtual_path="/",
        owner_id="user1"
    )
    
    mock_blob.generation = "12345"
    
    file_version = service.upload_file(file_content, file_model, "user1")
    
    mock_bucket.blob.assert_called_with("user1/files/test.txt")
    mock_blob.upload_from_string.assert_called_once_with(
        file_content,
        content_type="text/plain"
    )
    assert file_version.version_id == "12345"

def test_download_file(mock_storage_client):
    """Test file download."""
    _, mock_bucket, mock_blob = mock_storage_client
    service = GCPStorageService(project_id="test-project", bucket_name="test-bucket")

    mock_blob.download_as_bytes.return_value = b"file content"
    content, metadata = service.download_file("storage_key")

    mock_bucket.blob.assert_called_with("storage_key")
    mock_blob.download_as_bytes.assert_called_once()
    assert content == b"file content"

def test_delete_file(mock_storage_client):
    """Test file soft delete."""
    _, mock_bucket, mock_blob = mock_storage_client
    service = GCPStorageService(project_id="test-project", bucket_name="test-bucket")

    result = service.delete_file("storage_key")

    mock_bucket.blob.assert_called_with("storage_key")
    mock_blob.patch.assert_called_once()
    assert result is True

def test_list_files(mock_storage_client):
    """Test listing files."""
    mock_client, _, _ = mock_storage_client
    service = GCPStorageService(project_id="test-project", bucket_name="test-bucket")

    mock_blob1 = MagicMock()
    mock_blob1.name = "user1/files/test1.txt"
    mock_blob1.metadata = {'owner_id': 'user1', 'display_name': 'test1.txt', 'virtual_path': '/'}

    mock_blob2 = MagicMock()
    mock_blob2.name = "user1/files/test2.txt"
    mock_blob2.metadata = {'owner_id': 'user1', 'display_name': 'test2.txt', 'virtual_path': '/'}

    mock_client.list_blobs.return_value = [mock_blob1, mock_blob2]

    files = service.list_files(prefix="user1/files/", owner_id="user1")

    assert len(files) == 2
    assert files[0].display_name == "test1.txt"


    def test_get_file_versions(mock_storage_client):
        """Test getting file versions."""
        mock_client, mock_bucket, _ = mock_storage_client
        service = GCPStorageService(project_id="test-project", bucket_name="test-bucket")
    
        mock_version1 = MagicMock()
        mock_version1.name = "storage_key"
        mock_version1.generation = "1"
        mock_version1.time_created = datetime.now(timezone.utc)
        mock_version1.metadata = {'created_by': 'user1', 'operation_type': 'upload'}
        mock_version1.size = 1024
    
        mock_version2 = MagicMock()
        mock_version2.name = "storage_key"
        mock_version2.generation = "2"
        mock_version2.time_created = datetime.now(timezone.utc)
        mock_version2.metadata = {'created_by': 'user1', 'operation_type': 'edit'}
        mock_version2.size = 2048
    
        mock_bucket.get_blob.return_value = mock_version2
        mock_client.list_blobs.return_value = [mock_version1, mock_version2]
    
        versions = service.get_file_versions("storage_key")
    
        assert len(versions) == 2
        assert versions[0].version_id == "2"
