from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import re


@dataclass
class File:
    """
    Represents a logical file with version history in the system.
    """
    display_name: str
    storage_key: str
    content_type: str
    virtual_path: str
    owner_id: str
    current_version_id: Optional[str] = None
    created_at: Optional[datetime] = None
    is_deleted: bool = False

    def __post_init__(self):
        """Validate file data after initialization."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()

        self.validate()

    def validate(self):
        """Validate file fields according to business rules."""
        # Display name validation
        if not self.display_name:
            raise ValueError("Display name is required")

        if len(self.display_name) > 255:
            raise ValueError("Display name must be 255 characters or less")

        # Check for path separators in filename
        if '/' in self.display_name or '\\' in self.display_name:
            raise ValueError("Display name cannot contain path separators")

        # Storage key validation
        if not self.storage_key:
            raise ValueError("Storage key is required")

        # Content type validation
        if not self.content_type:
            raise ValueError("Content type is required")

        # Virtual path validation
        if not self.virtual_path:
            raise ValueError("Virtual path is required")

        if not self.virtual_path.startswith('/'):
            raise ValueError("Virtual path must start with '/'")

        if not self.virtual_path.endswith('/'):
            raise ValueError("Virtual path must end with '/'")

        # Check for valid path format
        if '//' in self.virtual_path:
            raise ValueError("Virtual path cannot contain double slashes")

        # Owner ID validation
        if not self.owner_id:
            raise ValueError("Owner ID is required for all operations")

    def get_full_path(self) -> str:
        """Get the full virtual path including filename."""
        return f"{self.virtual_path}{self.display_name}"

    def get_folder_path(self) -> str:
        """Get the folder path without filename."""
        return self.virtual_path

    def mark_as_deleted(self):
        """Mark file as deleted (soft delete)."""
        self.is_deleted = True

    def restore(self):
        """Restore file from deleted state."""
        self.is_deleted = False

    def update_current_version(self, version_id: str):
        """Update the current version ID."""
        if not version_id:
            raise ValueError("Version ID cannot be empty")
        self.current_version_id = version_id

    def to_dict(self) -> dict:
        """Convert file to dictionary representation."""
        return {
            'file_id': self.storage_key,
            'display_name': self.display_name,
            'content_type': self.content_type,
            'virtual_path': self.virtual_path,
            'owner_id': self.owner_id,
            'current_version_id': self.current_version_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_deleted': self.is_deleted
        }

    @classmethod
    def from_gcp_metadata(cls, storage_key: str, metadata: dict, blob_info: dict) -> 'File':
        """Create File instance from GCP Cloud Storage metadata."""
        return cls(
            display_name=metadata.get('display_name', storage_key.split('/')[-1]),
            storage_key=storage_key,
            content_type=blob_info.get('content_type', 'application/octet-stream'),
            virtual_path=metadata.get('virtual_path', '/'),
            owner_id=metadata.get('owner_id', 'unknown'),
            current_version_id=blob_info.get('generation'),
            created_at=blob_info.get('time_created'),
            is_deleted=metadata.get('is_deleted', 'false').lower() == 'true'
        )

    def to_gcp_metadata(self) -> dict:
        """Convert file to GCP metadata format."""
        return {
            'display_name': self.display_name,
            'virtual_path': self.virtual_path,
            'owner_id': self.owner_id,
            'is_deleted': str(self.is_deleted).lower(),
            'created_at': self.created_at.isoformat() if self.created_at else ''
        }