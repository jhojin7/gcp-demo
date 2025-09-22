import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import os
import uuid

from models.file import File
from models.file_version import FileVersion
from models.user import User
from models.folder import Folder
from models.operation import Operation
from gcp_storage import GCPStorageService


class FileService:
    """
    Service layer for file operations, providing business logic on top of GCP Storage.
    Handles file lifecycle, ownership, and folder organization.
    """

    def __init__(self, gcp_service: GCPStorageService):
        """
        Initialize file service with GCP storage backend.

        Args:
            gcp_service: Configured GCP Storage service instance
        """
        self.gcp_service = gcp_service
        self.logger = logging.getLogger(__name__)

    def upload_file(self, file_content: bytes, filename: str, virtual_path: str,
                   user: User, content_type: str = None) -> Tuple[File, FileVersion, Operation]:
        """
        Upload a new file or create new version of existing file.

        Args:
            file_content: Binary file content
            filename: Original filename
            virtual_path: Target folder path
            user: User performing the upload
            content_type: MIME type (auto-detected if None)

        Returns:
            Tuple of (File, FileVersion, Operation)

        Raises:
            ValueError: For validation errors
            RuntimeError: For upload failures
        """
        try:
            # Auto-detect content type if not provided
            if content_type is None:
                content_type = self._detect_content_type(filename)

            # Normalize virtual path
            virtual_path = self._normalize_virtual_path(virtual_path)

            # Generate unique storage key
            storage_key = self._generate_storage_key(user.user_id, virtual_path, filename)

            # Check if file already exists
            existing_file = self._get_file_by_path(virtual_path + filename, user.user_id)

            if existing_file:
                # Create new version of existing file
                file_obj = existing_file
                operation_type = 'edit'
                self.logger.info(f"Creating new version of existing file: {storage_key}")
            else:
                # Create new file
                file_obj = File(
                    display_name=filename,
                    storage_key=storage_key,
                    content_type=content_type,
                    virtual_path=virtual_path,
                    owner_id=user.user_id
                )
                operation_type = 'upload'
                self.logger.info(f"Creating new file: {storage_key}")

            # Upload to GCP
            file_version = self.gcp_service.upload_file(
                file_content=file_content,
                file=file_obj,
                user_id=user.user_id,
                operation_type=operation_type
            )

            # Create operation record
            operation = Operation.create_upload_operation(
                user_id=user.user_id,
                file_storage_key=storage_key,
                version_id=file_version.version_id
            )

            self.logger.info(f"File upload successful: {filename} -> {storage_key}")
            return file_obj, file_version, operation

        except Exception as e:
            self.logger.error(f"File upload failed: {e}")
            raise

    def download_file(self, file_id: str, user: User, version_id: str = None) -> Tuple[bytes, str, Operation]:
        """
        Download file content.

        Args:
            file_id: File storage key or display name
            user: User requesting download
            version_id: Specific version (None for current)

        Returns:
            Tuple of (content, filename, operation)

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If user doesn't have access
            RuntimeError: For download failures
        """
        try:
            # Get file info
            file_obj = self._get_file_by_id_or_path(file_id, user.user_id)
            if not file_obj:
                raise FileNotFoundError(f"File not found: {file_id}")

            # Check ownership
            if not self._check_file_access(file_obj, user):
                raise PermissionError(f"Access denied to file: {file_id}")

            # Download from GCP
            content, metadata = self.gcp_service.download_file(
                storage_key=file_obj.storage_key,
                version_id=version_id
            )

            # Determine download filename
            if version_id:
                # Get version info for filename
                versions = self.gcp_service.get_file_versions(file_obj.storage_key)
                version_obj = next((v for v in versions if v.version_id == version_id), None)
                if version_obj:
                    filename = version_obj.get_display_name_with_version(file_obj.display_name)
                else:
                    filename = f"{file_obj.display_name}_v{version_id}"
            else:
                filename = file_obj.display_name

            # Create operation record
            operation = Operation.create_download_operation(
                user_id=user.user_id,
                file_storage_key=file_obj.storage_key,
                version_id=version_id
            )

            self.logger.info(f"File download successful: {file_obj.storage_key}")
            return content, filename, operation

        except Exception as e:
            self.logger.error(f"File download failed: {e}")
            raise

    def delete_file(self, file_id: str, user: User) -> Operation:
        """
        Soft delete a file (preserves version history).

        Args:
            file_id: File storage key or display name
            user: User performing deletion

        Returns:
            Operation: Deletion operation record

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If user doesn't have access
            RuntimeError: For deletion failures
        """
        try:
            # Get file info
            file_obj = self._get_file_by_id_or_path(file_id, user.user_id)
            if not file_obj:
                raise FileNotFoundError(f"File not found: {file_id}")

            # Check ownership
            if not self._check_file_access(file_obj, user):
                raise PermissionError(f"Access denied to file: {file_id}")

            # Check if already deleted
            if file_obj.is_deleted:
                raise ValueError(f"File already deleted: {file_id}")

            # Delete in GCP (soft delete)
            self.gcp_service.delete_file(file_obj.storage_key)

            # Update file object
            file_obj.mark_as_deleted()

            # Create operation record
            operation = Operation.create_delete_operation(
                user_id=user.user_id,
                file_storage_key=file_obj.storage_key
            )

            self.logger.info(f"File deletion successful: {file_obj.storage_key}")
            return operation

        except Exception as e:
            self.logger.error(f"File deletion failed: {e}")
            raise

    def restore_file_version(self, file_id: str, version_id: str, user: User) -> Tuple[File, FileVersion, Operation]:
        """
        Restore a file to a previous version.

        Args:
            file_id: File storage key or display name
            version_id: Version to restore
            user: User performing restoration

        Returns:
            Tuple of (File, new FileVersion, Operation)

        Raises:
            FileNotFoundError: If file or version doesn't exist
            PermissionError: If user doesn't have access
            RuntimeError: For restoration failures
        """
        try:
            # Get file info
            file_obj = self._get_file_by_id_or_path(file_id, user.user_id)
            if not file_obj:
                raise FileNotFoundError(f"File not found: {file_id}")

            # Check ownership
            if not self._check_file_access(file_obj, user):
                raise PermissionError(f"Access denied to file: {file_id}")

            # Get content from the version to restore
            content, metadata = self.gcp_service.download_file(
                storage_key=file_obj.storage_key,
                version_id=version_id
            )

            # If file was deleted, restore it
            if file_obj.is_deleted:
                file_obj.restore()

            # Upload as new version (restore operation)
            file_version = self.gcp_service.upload_file(
                file_content=content,
                file=file_obj,
                user_id=user.user_id,
                operation_type='restore',
                restore_source_version=version_id
            )

            # Create operation record
            operation = Operation.create_restore_operation(
                user_id=user.user_id,
                file_storage_key=file_obj.storage_key,
                version_id=version_id
            )

            self.logger.info(f"File restoration successful: {file_obj.storage_key} from version {version_id}")
            return file_obj, file_version, operation

        except Exception as e:
            self.logger.error(f"File restoration failed: {e}")
            raise

    def list_files(self, virtual_path: str, user: User, include_deleted: bool = False) -> List[File]:
        """
        List files in a specific folder.

        Args:
            virtual_path: Folder path to list
            user: User requesting list
            include_deleted: Include soft-deleted files

        Returns:
            List of File objects

        Raises:
            RuntimeError: For listing failures
        """
        try:
            # Normalize virtual path
            virtual_path = self._normalize_virtual_path(virtual_path)

            # Build prefix for GCP listing
            prefix = self._build_storage_prefix(user.user_id, virtual_path)

            # Get files from GCP
            files = self.gcp_service.list_files(
                prefix=prefix,
                owner_id=user.user_id,
                include_deleted=include_deleted
            )

            # Filter to exact folder match (not subfolders)
            filtered_files = []
            for file_obj in files:
                if file_obj.virtual_path == virtual_path:
                    filtered_files.append(file_obj)

            # Sort by display name
            filtered_files.sort(key=lambda f: f.display_name.lower())

            self.logger.info(f"Listed {len(filtered_files)} files in {virtual_path}")
            return filtered_files

        except Exception as e:
            self.logger.error(f"File listing failed: {e}")
            raise

    def get_folders_in_path(self, virtual_path: str, user: User) -> List[Folder]:
        """
        Get subfolders in a specific path.

        Args:
            virtual_path: Parent folder path
            user: User requesting folders

        Returns:
            List of Folder objects

        Raises:
            RuntimeError: For listing failures
        """
        try:
            # Normalize virtual path
            virtual_path = self._normalize_virtual_path(virtual_path)

            # Build prefix for GCP listing
            prefix = self._build_storage_prefix(user.user_id, virtual_path)

            # Get all files with this prefix
            all_files = self.gcp_service.list_files(
                prefix=prefix,
                owner_id=user.user_id,
                include_deleted=False
            )

            # Extract unique subfolder paths
            subfolder_paths = set()
            for file_obj in all_files:
                file_path = file_obj.virtual_path
                if file_path.startswith(virtual_path) and file_path != virtual_path:
                    # Find first subfolder
                    relative_path = file_path[len(virtual_path):]
                    if '/' in relative_path:
                        subfolder = relative_path.split('/')[0]
                        subfolder_paths.add(virtual_path + subfolder + '/')

            # Create Folder objects
            folders = []
            for folder_path in sorted(subfolder_paths):
                folder = Folder(
                    virtual_path=folder_path,
                    owner_id=user.user_id
                )
                folders.append(folder)

            self.logger.info(f"Found {len(folders)} subfolders in {virtual_path}")
            return folders

        except Exception as e:
            self.logger.error(f"Folder listing failed: {e}")
            raise

    def get_file_info(self, file_id: str, user: User) -> Optional[Dict[str, Any]]:
        """
        Get detailed file information.

        Args:
            file_id: File storage key or display name
            user: User requesting info

        Returns:
            Dict with file information or None if not found

        Raises:
            PermissionError: If user doesn't have access
        """
        try:
            # Get file info
            file_obj = self._get_file_by_id_or_path(file_id, user.user_id)
            if not file_obj:
                return None

            # Check ownership
            if not self._check_file_access(file_obj, user):
                raise PermissionError(f"Access denied to file: {file_id}")

            # Get GCP info
            gcp_info = self.gcp_service.get_file_info(file_obj.storage_key)
            if not gcp_info:
                return None

            # Combine information
            info = {
                **file_obj.to_dict(),
                'storage_info': gcp_info,
                'version_count': len(self.gcp_service.get_file_versions(file_obj.storage_key))
            }

            return info

        except Exception as e:
            self.logger.error(f"Get file info failed: {e}")
            raise

    def _get_file_by_id_or_path(self, file_id: str, owner_id: str) -> Optional[File]:
        """Get file by storage key or by searching display name."""
        # First try as storage key
        if self.gcp_service.file_exists(file_id):
            gcp_info = self.gcp_service.get_file_info(file_id)
            if gcp_info and gcp_info['metadata'].get('owner_id') == owner_id:
                return File.from_gcp_metadata(
                    storage_key=file_id,
                    metadata=gcp_info['metadata'],
                    blob_info=gcp_info
                )

        # Try searching by display name in all user's files
        all_files = self.gcp_service.list_files(owner_id=owner_id, include_deleted=True)
        for file_obj in all_files:
            if file_obj.display_name == file_id:
                return file_obj

        return None

    def _get_file_by_path(self, full_path: str, owner_id: str) -> Optional[File]:
        """Get file by full virtual path."""
        # Split path into folder and filename
        virtual_path = os.path.dirname(full_path) + '/'
        filename = os.path.basename(full_path)

        # List files in folder
        files = self.list_files(virtual_path, User(owner_id, "temp"))
        for file_obj in files:
            if file_obj.display_name == filename:
                return file_obj

        return None

    def _check_file_access(self, file_obj: File, user: User) -> bool:
        """Check if user has access to file."""
        return file_obj.owner_id == user.user_id

    def _normalize_virtual_path(self, virtual_path: str) -> str:
        """Normalize virtual path format."""
        if not virtual_path:
            return '/'

        # Ensure starts with /
        if not virtual_path.startswith('/'):
            virtual_path = '/' + virtual_path

        # Ensure ends with /
        if not virtual_path.endswith('/'):
            virtual_path += '/'

        # Remove double slashes
        while '//' in virtual_path:
            virtual_path = virtual_path.replace('//', '/')

        return virtual_path

    def _generate_storage_key(self, user_id: str, virtual_path: str, filename: str) -> str:
        """Generate unique storage key for file."""
        # Create unique identifier
        unique_id = str(uuid.uuid4())[:8]

        # Sanitize filename for storage
        safe_filename = self._sanitize_filename(filename)

        # Build storage key: user_id/files/virtual_path/unique_id-filename
        storage_path = virtual_path.strip('/')
        if storage_path:
            return f"{user_id}/files/{storage_path}/{unique_id}-{safe_filename}"
        else:
            return f"{user_id}/files/{unique_id}-{safe_filename}"

    def _build_storage_prefix(self, user_id: str, virtual_path: str) -> str:
        """Build GCS prefix for listing files in folder."""
        storage_path = virtual_path.strip('/')
        if storage_path:
            return f"{user_id}/files/{storage_path}/"
        else:
            return f"{user_id}/files/"

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe storage."""
        # Remove or replace problematic characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        sanitized = ''.join(c if c in safe_chars else '_' for c in filename)

        # Ensure not empty
        if not sanitized:
            sanitized = 'file'

        return sanitized

    def _detect_content_type(self, filename: str) -> str:
        """Detect MIME type from filename extension."""
        import mimetypes
        content_type, _ = mimetypes.guess_type(filename)
        return content_type or 'application/octet-stream'