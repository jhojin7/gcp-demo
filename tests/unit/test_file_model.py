import pytest
from datetime import datetime, timezone
from models.file import File

def test_file_creation():
    """Test successful creation of a File object."""
    now = datetime.now(timezone.utc)
    file = File(
        display_name="test.txt",
        storage_key="user1/files/test.txt",
        content_type="text/plain",
        virtual_path="/",
        owner_id="user1",
        created_at=now
    )
    assert file.display_name == "test.txt"
    assert file.storage_key == "user1/files/test.txt"
    assert file.content_type == "text/plain"
    assert file.virtual_path == "/"
    assert file.owner_id == "user1"
    assert file.created_at == now
    assert not file.is_deleted

def test_file_validation():
    """Test validation logic for File model."""
    with pytest.raises(ValueError, match="Display name is required"):
        File(display_name="", storage_key="key", content_type="type", virtual_path="/", owner_id="user")

    with pytest.raises(ValueError, match="Display name cannot contain path separators"):
        File(display_name="a/b.txt", storage_key="key", content_type="type", virtual_path="/", owner_id="user")

    with pytest.raises(ValueError, match="Virtual path must start with '/'"):
        File(display_name="a.txt", storage_key="key", content_type="type", virtual_path="a/", owner_id="user")

    with pytest.raises(ValueError, match="Virtual path must end with '/'"):
        File(display_name="a.txt", storage_key="key", content_type="type", virtual_path="/a", owner_id="user")

def test_file_path_methods():
    """Test get_full_path and get_folder_path methods."""
    file = File(
        display_name="test.txt",
        storage_key="key",
        content_type="type",
        virtual_path="/docs/",
        owner_id="user"
    )
    assert file.get_full_path() == "/docs/test.txt"
    assert file.get_folder_path() == "/docs/"

def test_file_state_change():
    """Test mark_as_deleted and restore methods."""
    file = File(display_name="a.txt", storage_key="key", content_type="type", virtual_path="/", owner_id="user")
    assert not file.is_deleted
    file.mark_as_deleted()
    assert file.is_deleted
    file.restore()
    assert not file.is_deleted

def test_update_current_version():
    """Test update_current_version method."""
    file = File(display_name="a.txt", storage_key="key", content_type="type", virtual_path="/", owner_id="user")
    assert file.current_version_id is None
    file.update_current_version("v1")
    assert file.current_version_id == "v1"
    with pytest.raises(ValueError, match="Version ID cannot be empty"):
        file.update_current_version("")

def test_to_dict():
    """Test to_dict method."""
    now = datetime.now(timezone.utc)
    file = File(
        display_name="test.txt",
        storage_key="key123",
        content_type="text/plain",
        virtual_path="/",
        owner_id="user1",
        current_version_id="v1",
        created_at=now
    )
    file_dict = file.to_dict()
    assert file_dict['file_id'] == "key123"
    assert file_dict['display_name'] == "test.txt"
    assert file_dict['content_type'] == "text/plain"
    assert file_dict['virtual_path'] == "/"
    assert file_dict['owner_id'] == "user1"
    assert file_dict['current_version_id'] == "v1"
    assert file_dict['created_at'] == now.isoformat()
    assert not file_dict['is_deleted']

def test_from_gcp_metadata():
    """Test from_gcp_metadata class method."""
    now = datetime.now(timezone.utc)
    metadata = {
        'display_name': 'doc.pdf',
        'virtual_path': '/pdfs/',
        'owner_id': 'user2',
        'is_deleted': 'true'
    }
    blob_info = {
        'content_type': 'application/pdf',
        'generation': '12345',
        'time_created': now
    }
    file = File.from_gcp_metadata("storage/key", metadata, blob_info)
    assert file.display_name == "doc.pdf"
    assert file.storage_key == "storage/key"
    assert file.content_type == "application/pdf"
    assert file.virtual_path == "/pdfs/"
    assert file.owner_id == "user2"
    assert file.current_version_id == "12345"
    assert file.created_at == now
    assert file.is_deleted

def test_to_gcp_metadata():
    """Test to_gcp_metadata method."""
    now = datetime.now(timezone.utc)
    file = File(
        display_name="image.png",
        storage_key="key",
        content_type="image/png",
        virtual_path="/images/",
        owner_id="user3",
        created_at=now
    )
    metadata = file.to_gcp_metadata()
    assert metadata['display_name'] == "image.png"
    assert metadata['virtual_path'] == "/images/"
    assert metadata['owner_id'] == "user3"
    assert metadata['is_deleted'] == 'false'
    assert metadata['created_at'] == now.isoformat()