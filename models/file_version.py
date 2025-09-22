from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta


@dataclass
class FileVersion:
    """
    Immutable snapshot of file content and metadata.
    """
    version_id: str
    file_storage_key: str
    size_bytes: int
    created_at: datetime
    created_by: str
    operation_type: str
    is_current: bool = False
    checksum: Optional[str] = None
    restore_source_version: Optional[str] = None

    def __post_init__(self):
        """Validate version data after initialization."""
        self.validate()

    def validate(self):
        """Validate file version fields according to business rules."""
        # Version ID validation
        if not self.version_id:
            raise ValueError("Version ID is required")

        # File storage key validation
        if not self.file_storage_key:
            raise ValueError("File storage key is required")

        # Size validation
        if self.size_bytes < 0:
            raise ValueError("Size bytes must be positive integer")

        # Operation type validation
        valid_operations = ['upload', 'restore', 'edit']
        if self.operation_type not in valid_operations:
            raise ValueError(f"Operation type must be one of: {valid_operations}")

        # Created by validation
        if not self.created_by:
            raise ValueError("Created by user is required")

        # Restore source validation
        if self.operation_type == 'restore' and not self.restore_source_version:
            raise ValueError("Restore source version required when operation_type is restore")

    def get_relative_time(self) -> str:
        """Get human-readable relative timestamp."""
        now = datetime.utcnow()
        diff = now - self.created_at

        # Handle future dates (shouldn't happen, but be safe)
        if diff.total_seconds() < 0:
            return "in the future"

        # Less than a minute
        if diff.total_seconds() < 60:
            seconds = int(diff.total_seconds())
            return f"{seconds} second{'s' if seconds != 1 else ''} ago"

        # Less than an hour
        if diff.total_seconds() < 3600:
            minutes = int(diff.total_seconds() / 60)
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"

        # Less than a day
        if diff.days == 0:
            hours = int(diff.total_seconds() / 3600)
            return f"{hours} hour{'s' if hours != 1 else ''} ago"

        # Less than a week
        if diff.days < 7:
            if diff.days == 1:
                return "Yesterday"
            return f"{diff.days} days ago"

        # Less than a month
        if diff.days < 30:
            weeks = diff.days // 7
            return f"{weeks} week{'s' if weeks != 1 else ''} ago"

        # Less than a year
        if diff.days < 365:
            months = diff.days // 30
            return f"{months} month{'s' if months != 1 else ''} ago"

        # Years
        years = diff.days // 365
        return f"{years} year{'s' if years != 1 else ''} ago"

    def to_dict(self) -> dict:
        """Convert file version to dictionary representation."""
        return {
            'version_id': self.version_id,
            'file_storage_key': self.file_storage_key,
            'size_bytes': self.size_bytes,
            'created_at': self.created_at.isoformat(),
            'created_by': self.created_by,
            'operation_type': self.operation_type,
            'is_current': self.is_current,
            'checksum': self.checksum,
            'restore_source_version': self.restore_source_version,
            'relative_time': self.get_relative_time()
        }

    @classmethod
    def from_gcp_blob(cls, blob, metadata: dict) -> 'FileVersion':
        """Create FileVersion instance from GCP Cloud Storage blob."""
        return cls(
            version_id=str(blob.generation),
            file_storage_key=blob.name,
            size_bytes=blob.size or 0,
            created_at=blob.time_created.replace(tzinfo=None) if blob.time_created else datetime.utcnow(),
            created_by=metadata.get('created_by', 'unknown'),
            operation_type=metadata.get('operation_type', 'upload'),
            is_current=blob.generation == blob.bucket.get_blob(blob.name).generation,
            checksum=blob.md5_hash,
            restore_source_version=metadata.get('restore_source_version')
        )

    def to_gcp_metadata(self) -> dict:
        """Convert file version to GCP metadata format."""
        metadata = {
            'created_by': self.created_by,
            'operation_type': self.operation_type,
            'created_at_iso': self.created_at.isoformat()
        }

        if self.restore_source_version:
            metadata['restore_source_version'] = self.restore_source_version

        return metadata

    def is_restore_operation(self) -> bool:
        """Check if this version was created by a restore operation."""
        return self.operation_type == 'restore'

    def get_display_name_with_version(self, original_name: str) -> str:
        """Get display name that includes version information."""
        if self.is_current:
            return original_name

        # For historical versions, include version identifier
        name_parts = original_name.rsplit('.', 1)
        if len(name_parts) == 2:
            name, ext = name_parts
            return f"{name}_v{self.version_id}.{ext}"
        else:
            return f"{original_name}_v{self.version_id}"

    def __lt__(self, other):
        """Enable sorting by creation time (newest first)."""
        if not isinstance(other, FileVersion):
            return NotImplemented
        return self.created_at > other.created_at  # Reverse order for newest first