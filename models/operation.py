from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import uuid


@dataclass
class Operation:
    """
    Audit record for tracking user actions and system events.
    """
    operation_type: str
    user_id: str
    timestamp: datetime
    file_storage_key: Optional[str] = None
    version_id: Optional[str] = None
    operation_id: Optional[str] = None
    ip_address: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None

    def __post_init__(self):
        """Validate operation data after initialization."""
        # Generate operation ID if not provided
        if self.operation_id is None:
            self.operation_id = str(uuid.uuid4())

        self.validate()

    def validate(self):
        """Validate operation fields according to business rules."""
        # Required fields validation
        if not self.user_id:
            raise ValueError("All operations must include user_id")

        if not self.timestamp:
            raise ValueError("All operations must include timestamp")

        if not self.operation_type:
            raise ValueError("Operation type is required")

        # Operation type validation
        valid_operations = ['upload', 'download', 'delete', 'restore', 'view', 'list', 'create_folder']
        if self.operation_type not in valid_operations:
            raise ValueError(f"Operation type must be one of: {valid_operations}")

        # Error handling validation
        if not self.success and not self.error_message:
            raise ValueError("Error message required when success is false")

        # Version-specific operations validation
        version_specific_ops = ['download', 'restore']
        if self.operation_type in version_specific_ops and not self.version_id:
            # Allow download without version_id for current version
            if self.operation_type == 'download':
                pass  # Current version download is acceptable
            else:
                raise ValueError(f"Version ID required for {self.operation_type} operations")

    def mark_as_failed(self, error_message: str):
        """Mark operation as failed with error details."""
        self.success = False
        self.error_message = error_message

    def mark_as_successful(self):
        """Mark operation as successful."""
        self.success = True
        self.error_message = None

    def is_file_operation(self) -> bool:
        """Check if this operation targets a specific file."""
        return bool(self.file_storage_key)

    def is_version_specific(self) -> bool:
        """Check if this operation targets a specific version."""
        return bool(self.version_id)

    def get_duration_ms(self, end_time: datetime = None) -> int:
        """Calculate operation duration in milliseconds."""
        if end_time is None:
            end_time = datetime.utcnow()

        delta = end_time - self.timestamp
        return int(delta.total_seconds() * 1000)

    def to_dict(self) -> dict:
        """Convert operation to dictionary representation."""
        return {
            'operation_id': self.operation_id,
            'operation_type': self.operation_type,
            'file_storage_key': self.file_storage_key,
            'version_id': self.version_id,
            'user_id': self.user_id,
            'timestamp': self.timestamp.isoformat(),
            'ip_address': self.ip_address,
            'success': self.success,
            'error_message': self.error_message,
            'is_file_operation': self.is_file_operation(),
            'is_version_specific': self.is_version_specific()
        }

    def to_audit_log_entry(self) -> dict:
        """Convert operation to audit log format."""
        log_entry = {
            'timestamp': self.timestamp.isoformat(),
            'operation_id': self.operation_id,
            'user_id': self.user_id,
            'operation': self.operation_type,
            'success': self.success
        }

        # Add optional fields if present
        if self.file_storage_key:
            log_entry['file'] = self.file_storage_key

        if self.version_id:
            log_entry['version'] = self.version_id

        if self.ip_address:
            log_entry['source_ip'] = self.ip_address

        if self.error_message:
            log_entry['error'] = self.error_message

        return log_entry

    @classmethod
    def create_upload_operation(cls, user_id: str, file_storage_key: str, version_id: str, ip_address: str = None) -> 'Operation':
        """Create operation record for file upload."""
        return cls(
            operation_type='upload',
            user_id=user_id,
            timestamp=datetime.utcnow(),
            file_storage_key=file_storage_key,
            version_id=version_id,
            ip_address=ip_address
        )

    @classmethod
    def create_download_operation(cls, user_id: str, file_storage_key: str, version_id: str = None, ip_address: str = None) -> 'Operation':
        """Create operation record for file download."""
        return cls(
            operation_type='download',
            user_id=user_id,
            timestamp=datetime.utcnow(),
            file_storage_key=file_storage_key,
            version_id=version_id,
            ip_address=ip_address
        )

    @classmethod
    def create_delete_operation(cls, user_id: str, file_storage_key: str, ip_address: str = None) -> 'Operation':
        """Create operation record for file deletion."""
        return cls(
            operation_type='delete',
            user_id=user_id,
            timestamp=datetime.utcnow(),
            file_storage_key=file_storage_key,
            ip_address=ip_address
        )

    @classmethod
    def create_restore_operation(cls, user_id: str, file_storage_key: str, version_id: str, ip_address: str = None) -> 'Operation':
        """Create operation record for version restoration."""
        return cls(
            operation_type='restore',
            user_id=user_id,
            timestamp=datetime.utcnow(),
            file_storage_key=file_storage_key,
            version_id=version_id,
            ip_address=ip_address
        )

    @classmethod
    def create_view_operation(cls, user_id: str, file_storage_key: str = None, ip_address: str = None) -> 'Operation':
        """Create operation record for file/folder viewing."""
        return cls(
            operation_type='view',
            user_id=user_id,
            timestamp=datetime.utcnow(),
            file_storage_key=file_storage_key,
            ip_address=ip_address
        )

    @classmethod
    def create_list_operation(cls, user_id: str, ip_address: str = None) -> 'Operation':
        """Create operation record for file listing."""
        return cls(
            operation_type='list',
            user_id=user_id,
            timestamp=datetime.utcnow(),
            ip_address=ip_address
        )

    def __str__(self) -> str:
        """String representation of operation."""
        status = "SUCCESS" if self.success else "FAILED"
        return f"Operation({self.operation_type} by {self.user_id} at {self.timestamp} - {status})"

    def __lt__(self, other) -> bool:
        """Enable sorting by timestamp (newest first)."""
        if not isinstance(other, Operation):
            return NotImplemented
        return self.timestamp > other.timestamp  # Reverse order for newest first