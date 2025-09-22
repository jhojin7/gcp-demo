import pytest
from datetime import datetime, timedelta, timezone
from models.file_version import FileVersion

def test_file_version_creation():
    """Test successful creation of a FileVersion object."""
    now = datetime.now(timezone.utc)
    version = FileVersion(
        version_id="1",
        file_storage_key="user1/files/test.txt",
        size_bytes=1024,
        created_at=now,
        created_by="user1",
        operation_type="upload"
    )
    assert version.version_id == "1"
    assert version.size_bytes == 1024

def test_file_version_validation():
    """Test validation logic for FileVersion model."""
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="Version ID is required"):
        FileVersion(version_id="", file_storage_key="key", size_bytes=1, created_at=now, created_by="user", operation_type="upload")

    with pytest.raises(ValueError, match="Size bytes must be positive integer"):
        FileVersion(version_id="1", file_storage_key="key", size_bytes=-1, created_at=now, created_by="user", operation_type="upload")

    with pytest.raises(ValueError, match=r"Operation type must be one of: \['upload', 'restore', 'edit']"):
        FileVersion(version_id="1", file_storage_key="key", size_bytes=1, created_at=now, created_by="user", operation_type="delete")

    with pytest.raises(ValueError, match="Restore source version required when operation_type is restore"):
        FileVersion(version_id="1", file_storage_key="key", size_bytes=1, created_at=now, created_by="user", operation_type="restore")

def test_get_relative_time():
    """Test get_relative_time method."""
    now = datetime.now(timezone.utc)
    version = FileVersion(version_id="1", file_storage_key="key", size_bytes=1, created_at=now, created_by="user", operation_type="upload")
    assert "second" in version.get_relative_time()

    version.created_at = now - timedelta(minutes=5)
    assert version.get_relative_time() == "5 minutes ago"

    version.created_at = now - timedelta(hours=3)
    assert version.get_relative_time() == "3 hours ago"

    version.created_at = now - timedelta(days=1)
    assert version.get_relative_time() == "Yesterday"

    version.created_at = now - timedelta(days=10)
    assert version.get_relative_time() == "1 week ago"

    version.created_at = now - timedelta(days=40)
    assert version.get_relative_time() == "1 month ago"

    version.created_at = now - timedelta(days=400)
    assert version.get_relative_time() == "1 year ago"

def test_to_dict():
    """Test to_dict method."""
    now = datetime.now(timezone.utc)
    version = FileVersion(
        version_id="1",
        file_storage_key="key",
        size_bytes=123,
        created_at=now,
        created_by="user1",
        operation_type="upload",
        is_current=True,
        checksum="md5hash"
    )
    version_dict = version.to_dict()
    assert version_dict['version_id'] == "1"
    assert version_dict['size_bytes'] == 123
    assert "ago" in version_dict['relative_time']

def test_is_restore_operation():
    """Test is_restore_operation method."""
    now = datetime.now(timezone.utc)
    upload_version = FileVersion(version_id="1", file_storage_key="key", size_bytes=1, created_at=now, created_by="user", operation_type="upload")
    assert not upload_version.is_restore_operation()

    restore_version = FileVersion(version_id="2", file_storage_key="key", size_bytes=1, created_at=now, created_by="user", operation_type="restore", restore_source_version="1")
    assert restore_version.is_restore_operation()

def test_get_display_name_with_version():
    """Test get_display_name_with_version method."""
    now = datetime.now(timezone.utc)
    current_version = FileVersion(version_id="2", file_storage_key="key", size_bytes=1, created_at=now, created_by="user", operation_type="upload", is_current=True)
    assert current_version.get_display_name_with_version("test.txt") == "test.txt"

    historical_version = FileVersion(version_id="1", file_storage_key="key", size_bytes=1, created_at=now, created_by="user", operation_type="upload")
    assert historical_version.get_display_name_with_version("test.txt") == "test_v1.txt"
    assert historical_version.get_display_name_with_version("test") == "test_v1"