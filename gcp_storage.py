import os
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from google.cloud import storage
from google.cloud.exceptions import NotFound, Forbidden, BadRequest
from google.auth.exceptions import DefaultCredentialsError

from models.file import File
from models.file_version import FileVersion
from models.operation import Operation


class GCPStorageService:
    """
    Service class for Google Cloud Storage operations with versioning support.
    Handles authentication, file operations, and metadata management.
    """

    def __init__(self, project_id: str, bucket_name: str, service_account_key_path: str = None):
        """
        Initialize GCP Storage service.

        Args:
            project_id: GCP project ID
            bucket_name: GCS bucket name (must have versioning enabled)
            service_account_key_path: Optional path to service account JSON key
        """
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.service_account_key_path = service_account_key_path
        self.logger = logging.getLogger(__name__)

        # Initialize client and bucket
        self._client = None
        self._bucket = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize GCP Storage client with authentication."""
        try:
            if self.service_account_key_path and os.path.exists(self.service_account_key_path):
                # Use service account key file
                self._client = storage.Client.from_service_account_json(
                    self.service_account_key_path,
                    project=self.project_id
                )
                self.logger.info(f"Initialized GCP client with service account key")
            else:
                # Use default credentials (environment variables, metadata service, etc.)
                self._client = storage.Client(project=self.project_id)
                self.logger.info(f"Initialized GCP client with default credentials")

            # Get bucket reference
            self._bucket = self._client.bucket(self.bucket_name)

            # Verify bucket exists and has versioning enabled
            self._verify_bucket_configuration()

        except DefaultCredentialsError as e:
            self.logger.error(f"Authentication failed: {e}")
            raise ValueError(f"GCP authentication failed. Check credentials: {e}")
        except Exception as e:
            self.logger.error(f"Failed to initialize GCP client: {e}")
            raise ValueError(f"GCP client initialization failed: {e}")

    def _verify_bucket_configuration(self):
        """Verify bucket exists and has versioning enabled."""
        try:
            # Check if bucket exists and is accessible
            self._bucket.reload()

            # Check versioning status
            versioning_enabled = self._bucket.versioning_enabled
            if not versioning_enabled:
                self.logger.warning(f"Bucket {self.bucket_name} does not have versioning enabled")
                # Note: This is a warning, not an error, as we might want to enable it programmatically

            self.logger.info(f"Bucket {self.bucket_name} verified (versioning: {versioning_enabled})")

        except NotFound:
            raise ValueError(f"Bucket {self.bucket_name} not found or not accessible")
        except Forbidden:
            raise ValueError(f"Access denied to bucket {self.bucket_name}")
        except Exception as e:
            raise ValueError(f"Bucket verification failed: {e}")

    def upload_file(self, file_content: bytes, file: File, user_id: str,
                   operation_type: str = 'upload', restore_source_version: str = None) -> FileVersion:
        """
        Upload file content to GCS with metadata.

        Args:
            file_content: Binary file content
            file: File model with metadata
            user_id: User performing the upload
            operation_type: Type of operation (upload, restore, edit)
            restore_source_version: Source version for restore operations

        Returns:
            FileVersion: Created file version

        Raises:
            ValueError: For validation errors
            RuntimeError: For GCP operation failures
        """
        try:
            # Create blob reference
            blob = self._bucket.blob(file.storage_key)

            # Prepare metadata
            file_metadata = file.to_gcp_metadata()
            version_metadata = {
                'created_by': user_id,
                'operation_type': operation_type,
                'created_at_iso': datetime.utcnow().isoformat()
            }

            if restore_source_version:
                version_metadata['restore_source_version'] = restore_source_version

            # Combine metadata
            all_metadata = {**file_metadata, **version_metadata}

            # Set blob metadata
            blob.metadata = all_metadata

            # Upload content
            blob.upload_from_string(
                file_content,
                content_type=file.content_type
            )

            self.logger.info(f"Uploaded file {file.storage_key} (generation: {blob.generation})")

            # Create FileVersion instance
            file_version = FileVersion(
                version_id=str(blob.generation),
                file_storage_key=file.storage_key,
                size_bytes=len(file_content),
                created_at=datetime.utcnow(),
                created_by=user_id,
                operation_type=operation_type,
                is_current=True,
                checksum=blob.md5_hash,
                restore_source_version=restore_source_version
            )

            # Update file's current version
            file.update_current_version(str(blob.generation))

            return file_version

        except Exception as e:
            self.logger.error(f"Upload failed for {file.storage_key}: {e}")
            raise RuntimeError(f"File upload failed: {e}")

    def download_file(self, storage_key: str, version_id: str = None) -> Tuple[bytes, Dict[str, Any]]:
        """
        Download file content from GCS.

        Args:
            storage_key: GCS object key
            version_id: Specific version to download (None for current)

        Returns:
            Tuple of (file_content, metadata)

        Raises:
            FileNotFoundError: If file doesn't exist
            RuntimeError: For GCP operation failures
        """
        try:
            if version_id:
                # Download specific version
                blob = self._bucket.blob(storage_key, generation=int(version_id))
            else:
                # Download current version
                blob = self._bucket.blob(storage_key)

            # Check if blob exists
            if not blob.exists():
                raise FileNotFoundError(f"File {storage_key} not found")

            # Download content
            content = blob.download_as_bytes()

            # Get metadata
            metadata = {
                'content_type': blob.content_type,
                'size': blob.size,
                'generation': blob.generation,
                'time_created': blob.time_created,
                'md5_hash': blob.md5_hash,
                'custom_metadata': blob.metadata or {}
            }

            self.logger.info(f"Downloaded file {storage_key} (generation: {blob.generation}, size: {blob.size})")

            return content, metadata

        except NotFound:
            raise FileNotFoundError(f"File {storage_key} not found")
        except Exception as e:
            self.logger.error(f"Download failed for {storage_key}: {e}")
            raise RuntimeError(f"File download failed: {e}")

    def delete_file(self, storage_key: str) -> bool:
        """
        Soft delete file by updating metadata (preserves all versions).

        Args:
            storage_key: GCS object key

        Returns:
            bool: True if deletion successful

        Raises:
            FileNotFoundError: If file doesn't exist
            RuntimeError: For GCP operation failures
        """
        try:
            blob = self._bucket.blob(storage_key)

            if not blob.exists():
                raise FileNotFoundError(f"File {storage_key} not found")

            # Get current metadata
            blob.reload()
            current_metadata = blob.metadata or {}

            # Mark as deleted
            current_metadata['is_deleted'] = 'true'
            current_metadata['deleted_at'] = datetime.utcnow().isoformat()

            # Update metadata
            blob.metadata = current_metadata
            blob.patch()

            self.logger.info(f"Soft deleted file {storage_key}")
            return True

        except NotFound:
            raise FileNotFoundError(f"File {storage_key} not found")
        except Exception as e:
            self.logger.error(f"Delete failed for {storage_key}: {e}")
            raise RuntimeError(f"File deletion failed: {e}")

    def list_files(self, prefix: str = "", owner_id: str = None, include_deleted: bool = False) -> List[File]:
        """
        List files in bucket with optional filtering.

        Args:
            prefix: Path prefix to filter by
            owner_id: Filter by file owner
            include_deleted: Include soft-deleted files

        Returns:
            List of File objects

        Raises:
            RuntimeError: For GCP operation failures
        """
        try:
            # List blobs with prefix
            blobs = self._client.list_blobs(self._bucket, prefix=prefix)

            files = []
            for blob in blobs:
                # Skip if no metadata (shouldn't happen in our system)
                if not blob.metadata:
                    continue

                # Filter by owner if specified
                if owner_id and blob.metadata.get('owner_id') != owner_id:
                    continue

                # Filter deleted files if requested
                is_deleted = blob.metadata.get('is_deleted', 'false').lower() == 'true'
                if is_deleted and not include_deleted:
                    continue

                # Create File instance
                file = File.from_gcp_metadata(
                    storage_key=blob.name,
                    metadata=blob.metadata,
                    blob_info={
                        'content_type': blob.content_type,
                        'generation': blob.generation,
                        'time_created': blob.time_created
                    }
                )

                files.append(file)

            self.logger.info(f"Listed {len(files)} files with prefix '{prefix}'")
            return files

        except Exception as e:
            self.logger.error(f"List files failed: {e}")
            raise RuntimeError(f"File listing failed: {e}")

    def get_file_versions(self, storage_key: str) -> List[FileVersion]:
        """
        Get all versions of a specific file.

        Args:
            storage_key: GCS object key

        Returns:
            List of FileVersion objects sorted by creation time (newest first)

        Raises:
            FileNotFoundError: If file doesn't exist
            RuntimeError: For GCP operation failures
        """
        try:
            # List all versions of the blob
            blobs = self._client.list_blobs(
                self._bucket,
                prefix=storage_key,
                versions=True
            )

            versions = []
            current_generation = None

            # Get current version generation
            try:
                current_blob = self._bucket.blob(storage_key)
                if current_blob.exists():
                    current_generation = current_blob.generation
            except:
                pass

            for blob in blobs:
                # Only include exact matches (not prefix matches)
                if blob.name != storage_key:
                    continue

                # Create FileVersion instance
                metadata = blob.metadata or {}
                version = FileVersion(
                    version_id=str(blob.generation),
                    file_storage_key=blob.name,
                    size_bytes=blob.size or 0,
                    created_at=blob.time_created.replace(tzinfo=None) if blob.time_created else datetime.utcnow(),
                    created_by=metadata.get('created_by', 'unknown'),
                    operation_type=metadata.get('operation_type', 'upload'),
                    is_current=blob.generation == current_generation,
                    checksum=blob.md5_hash,
                    restore_source_version=metadata.get('restore_source_version')
                )

                versions.append(version)

            # Sort by creation time (newest first)
            versions.sort()

            self.logger.info(f"Found {len(versions)} versions for file {storage_key}")
            return versions

        except Exception as e:
            self.logger.error(f"Get versions failed for {storage_key}: {e}")
            raise RuntimeError(f"Get file versions failed: {e}")

    def file_exists(self, storage_key: str, version_id: str = None) -> bool:
        """
        Check if file exists in GCS.

        Args:
            storage_key: GCS object key
            version_id: Specific version to check (None for current)

        Returns:
            bool: True if file exists
        """
        try:
            if version_id:
                blob = self._bucket.blob(storage_key, generation=int(version_id))
            else:
                blob = self._bucket.blob(storage_key)

            return blob.exists()

        except Exception as e:
            self.logger.error(f"File exists check failed for {storage_key}: {e}")
            return False

    def get_file_info(self, storage_key: str) -> Optional[Dict[str, Any]]:
        """
        Get file information and metadata.

        Args:
            storage_key: GCS object key

        Returns:
            Dict with file information or None if not found
        """
        try:
            blob = self._bucket.blob(storage_key)

            if not blob.exists():
                return None

            blob.reload()

            return {
                'storage_key': blob.name,
                'content_type': blob.content_type,
                'size': blob.size,
                'generation': blob.generation,
                'time_created': blob.time_created,
                'time_updated': blob.updated,
                'md5_hash': blob.md5_hash,
                'metadata': blob.metadata or {}
            }

        except Exception as e:
            self.logger.error(f"Get file info failed for {storage_key}: {e}")
            return None

    def enable_bucket_versioning(self) -> bool:
        """
        Enable versioning on the bucket if not already enabled.

        Returns:
            bool: True if versioning is now enabled

        Raises:
            RuntimeError: If enabling versioning fails
        """
        try:
            if not self._bucket.versioning_enabled:
                self._bucket.versioning_enabled = True
                self._bucket.patch()
                self.logger.info(f"Enabled versioning on bucket {self.bucket_name}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to enable versioning: {e}")
            raise RuntimeError(f"Enable versioning failed: {e}")

    def get_bucket_info(self) -> Dict[str, Any]:
        """
        Get bucket information and configuration.

        Returns:
            Dict with bucket information
        """
        try:
            self._bucket.reload()

            return {
                'name': self._bucket.name,
                'location': self._bucket.location,
                'storage_class': self._bucket.storage_class,
                'versioning_enabled': self._bucket.versioning_enabled,
                'time_created': self._bucket.time_created,
                'project': self.project_id
            }

        except Exception as e:
            self.logger.error(f"Get bucket info failed: {e}")
            return {}