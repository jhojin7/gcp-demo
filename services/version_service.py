import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from models.file import File
from models.file_version import FileVersion
from models.user import User
from models.operation import Operation
from gcp_storage import GCPStorageService


class VersionService:
    """
    Service layer for file version management operations.
    Handles version history, comparisons, and version-specific operations.
    """

    def __init__(self, gcp_service: GCPStorageService):
        """
        Initialize version service with GCP storage backend.

        Args:
            gcp_service: Configured GCP Storage service instance
        """
        self.gcp_service = gcp_service
        self.logger = logging.getLogger(__name__)

    def get_version_history(self, file_id: str, user: User) -> List[FileVersion]:
        """
        Get complete version history for a file.

        Args:
            file_id: File storage key or display name
            user: User requesting history

        Returns:
            List of FileVersion objects sorted by creation time (newest first)

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If user doesn't have access
            RuntimeError: For operation failures
        """
        try:
            # Get file info first to check access
            file_obj = self._get_file_by_id_or_path(file_id, user.user_id)
            if not file_obj:
                raise FileNotFoundError(f"File not found: {file_id}")

            # Check ownership
            if not self._check_file_access(file_obj, user):
                raise PermissionError(f"Access denied to file: {file_id}")

            # Get versions from GCP
            versions = self.gcp_service.get_file_versions(file_obj.storage_key)

            # Enrich with additional context
            enriched_versions = []
            for version in versions:
                enriched_version = self._enrich_version_info(version, file_obj)
                enriched_versions.append(enriched_version)

            self.logger.info(f"Retrieved {len(enriched_versions)} versions for file {file_obj.storage_key}")
            return enriched_versions

        except Exception as e:
            self.logger.error(f"Get version history failed: {e}")
            raise

    def get_version_details(self, file_id: str, version_id: str, user: User) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific version.

        Args:
            file_id: File storage key or display name
            version_id: Specific version identifier
            user: User requesting details

        Returns:
            Dict with version details or None if not found

        Raises:
            PermissionError: If user doesn't have access
            RuntimeError: For operation failures
        """
        try:
            # Get file info first to check access
            file_obj = self._get_file_by_id_or_path(file_id, user.user_id)
            if not file_obj:
                return None

            # Check ownership
            if not self._check_file_access(file_obj, user):
                raise PermissionError(f"Access denied to file: {file_id}")

            # Get all versions and find the specific one
            versions = self.gcp_service.get_file_versions(file_obj.storage_key)
            target_version = next((v for v in versions if v.version_id == version_id), None)

            if not target_version:
                return None

            # Get GCP metadata for this version
            _, metadata = self.gcp_service.download_file(
                storage_key=file_obj.storage_key,
                version_id=version_id
            )

            # Build detailed info
            details = {
                **target_version.to_dict(),
                'file_info': file_obj.to_dict(),
                'storage_metadata': metadata,
                'download_filename': target_version.get_display_name_with_version(file_obj.display_name),
                'is_restorable': not target_version.is_current,
                'restore_chain': self._get_restore_chain(target_version, versions)
            }

            return details

        except Exception as e:
            self.logger.error(f"Get version details failed: {e}")
            raise

    def compare_versions(self, file_id: str, version1_id: str, version2_id: str, user: User) -> Dict[str, Any]:
        """
        Compare two versions of a file.

        Args:
            file_id: File storage key or display name
            version1_id: First version to compare
            version2_id: Second version to compare
            user: User requesting comparison

        Returns:
            Dict with comparison results

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If user doesn't have access
            ValueError: If versions don't exist
            RuntimeError: For operation failures
        """
        try:
            # Get file info first to check access
            file_obj = self._get_file_by_id_or_path(file_id, user.user_id)
            if not file_obj:
                raise FileNotFoundError(f"File not found: {file_id}")

            # Check ownership
            if not self._check_file_access(file_obj, user):
                raise PermissionError(f"Access denied to file: {file_id}")

            # Get version info
            versions = self.gcp_service.get_file_versions(file_obj.storage_key)
            version1 = next((v for v in versions if v.version_id == version1_id), None)
            version2 = next((v for v in versions if v.version_id == version2_id), None)

            if not version1:
                raise ValueError(f"Version {version1_id} not found")
            if not version2:
                raise ValueError(f"Version {version2_id} not found")

            # Basic comparison data
            comparison = {
                'file_info': file_obj.to_dict(),
                'version1': version1.to_dict(),
                'version2': version2.to_dict(),
                'size_difference': version2.size_bytes - version1.size_bytes,
                'time_difference': (version2.created_at - version1.created_at).total_seconds(),
                'same_content': version1.checksum == version2.checksum if version1.checksum and version2.checksum else None,
                'newer_version': version1_id if version1.created_at > version2.created_at else version2_id
            }

            # Add metadata comparison
            comparison['metadata_changes'] = self._compare_version_metadata(version1, version2)

            self.logger.info(f"Compared versions {version1_id} and {version2_id} for file {file_obj.storage_key}")
            return comparison

        except Exception as e:
            self.logger.error(f"Version comparison failed: {e}")
            raise

    def get_restore_preview(self, file_id: str, version_id: str, user: User) -> Dict[str, Any]:
        """
        Preview what would happen if a version is restored.

        Args:
            file_id: File storage key or display name
            version_id: Version to preview restoration
            user: User requesting preview

        Returns:
            Dict with restore preview information

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If user doesn't have access
            ValueError: If version doesn't exist
            RuntimeError: For operation failures
        """
        try:
            # Get file info first to check access
            file_obj = self._get_file_by_id_or_path(file_id, user.user_id)
            if not file_obj:
                raise FileNotFoundError(f"File not found: {file_id}")

            # Check ownership
            if not self._check_file_access(file_obj, user):
                raise PermissionError(f"Access denied to file: {file_id}")

            # Get version info
            versions = self.gcp_service.get_file_versions(file_obj.storage_key)
            target_version = next((v for v in versions if v.version_id == version_id), None)

            if not target_version:
                raise ValueError(f"Version {version_id} not found")

            current_version = next((v for v in versions if v.is_current), None)

            # Build preview
            preview = {
                'file_info': file_obj.to_dict(),
                'target_version': target_version.to_dict(),
                'current_version': current_version.to_dict() if current_version else None,
                'will_create_new_version': True,
                'is_already_current': target_version.is_current,
                'restore_source': version_id,
                'estimated_operation': {
                    'type': 'restore',
                    'user': user.user_id,
                    'timestamp': datetime.utcnow().isoformat()
                }
            }

            # Add change summary if current version exists
            if current_version and not target_version.is_current:
                preview['changes'] = {
                    'size_change': target_version.size_bytes - current_version.size_bytes,
                    'content_different': target_version.checksum != current_version.checksum,
                    'time_difference': (current_version.created_at - target_version.created_at).total_seconds()
                }

            self.logger.info(f"Generated restore preview for version {version_id} of file {file_obj.storage_key}")
            return preview

        except Exception as e:
            self.logger.error(f"Restore preview failed: {e}")
            raise

    def cleanup_old_versions(self, file_id: str, user: User, keep_count: int = 10) -> Dict[str, Any]:
        """
        Clean up old versions of a file (keeping specified number of recent versions).

        Args:
            file_id: File storage key or display name
            user: User performing cleanup
            keep_count: Number of recent versions to keep

        Returns:
            Dict with cleanup results

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If user doesn't have access
            RuntimeError: For operation failures
        """
        try:
            # Get file info first to check access
            file_obj = self._get_file_by_id_or_path(file_id, user.user_id)
            if not file_obj:
                raise FileNotFoundError(f"File not found: {file_id}")

            # Check ownership
            if not self._check_file_access(file_obj, user):
                raise PermissionError(f"Access denied to file: {file_id}")

            # Get version info
            versions = self.gcp_service.get_file_versions(file_obj.storage_key)

            # Sort by creation time (newest first) and identify versions to remove
            versions.sort()
            versions_to_keep = versions[:keep_count]
            versions_to_remove = versions[keep_count:]

            # For now, just return what would be removed (GCP doesn't easily support version deletion)
            # In a full implementation, you'd need to use lifecycle policies or bucket policies
            cleanup_result = {
                'file_info': file_obj.to_dict(),
                'total_versions': len(versions),
                'versions_to_keep': len(versions_to_keep),
                'versions_identified_for_cleanup': len(versions_to_remove),
                'keep_count_setting': keep_count,
                'cleanup_performed': False,
                'note': 'GCP version cleanup requires lifecycle policies - marking for future cleanup',
                'versions_marked_for_cleanup': [v.version_id for v in versions_to_remove]
            }

            self.logger.info(f"Identified {len(versions_to_remove)} versions for cleanup in file {file_obj.storage_key}")
            return cleanup_result

        except Exception as e:
            self.logger.error(f"Version cleanup failed: {e}")
            raise

    def get_version_statistics(self, file_id: str, user: User) -> Dict[str, Any]:
        """
        Get statistics about file versions.

        Args:
            file_id: File storage key or display name
            user: User requesting statistics

        Returns:
            Dict with version statistics

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If user doesn't have access
            RuntimeError: For operation failures
        """
        try:
            # Get file info first to check access
            file_obj = self._get_file_by_id_or_path(file_id, user.user_id)
            if not file_obj:
                raise FileNotFoundError(f"File not found: {file_id}")

            # Check ownership
            if not self._check_file_access(file_obj, user):
                raise PermissionError(f"Access denied to file: {file_id}")

            # Get version info
            versions = self.gcp_service.get_file_versions(file_obj.storage_key)

            if not versions:
                return {'error': 'No versions found'}

            # Calculate statistics
            total_size = sum(v.size_bytes for v in versions)
            sizes = [v.size_bytes for v in versions]
            operation_counts = {}

            for version in versions:
                op_type = version.operation_type
                operation_counts[op_type] = operation_counts.get(op_type, 0) + 1

            # Find version ranges
            oldest_version = min(versions, key=lambda v: v.created_at)
            newest_version = max(versions, key=lambda v: v.created_at)
            current_version = next((v for v in versions if v.is_current), newest_version)

            statistics = {
                'file_info': file_obj.to_dict(),
                'version_count': len(versions),
                'total_storage_size': total_size,
                'average_version_size': total_size // len(versions),
                'min_version_size': min(sizes),
                'max_version_size': max(sizes),
                'current_version_size': current_version.size_bytes,
                'operation_counts': operation_counts,
                'version_timeline': {
                    'first_version': oldest_version.to_dict(),
                    'latest_version': newest_version.to_dict(),
                    'current_version': current_version.to_dict(),
                    'days_span': (newest_version.created_at - oldest_version.created_at).days
                },
                'restore_operations': len([v for v in versions if v.operation_type == 'restore'])
            }

            return statistics

        except Exception as e:
            self.logger.error(f"Version statistics failed: {e}")
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

    def _check_file_access(self, file_obj: File, user: User) -> bool:
        """Check if user has access to file."""
        return file_obj.owner_id == user.user_id

    def _enrich_version_info(self, version: FileVersion, file_obj: File) -> FileVersion:
        """Add additional context to version information."""
        # Version object is already rich, but we could add more context here
        # For now, just return the version as-is
        return version

    def _compare_version_metadata(self, version1: FileVersion, version2: FileVersion) -> Dict[str, Any]:
        """Compare metadata between two versions."""
        changes = {}

        # Size comparison
        if version1.size_bytes != version2.size_bytes:
            changes['size'] = {
                'old': version1.size_bytes,
                'new': version2.size_bytes,
                'difference': version2.size_bytes - version1.size_bytes
            }

        # Operation type comparison
        if version1.operation_type != version2.operation_type:
            changes['operation_type'] = {
                'old': version1.operation_type,
                'new': version2.operation_type
            }

        # User comparison
        if version1.created_by != version2.created_by:
            changes['created_by'] = {
                'old': version1.created_by,
                'new': version2.created_by
            }

        # Time comparison
        time_diff = (version2.created_at - version1.created_at).total_seconds()
        changes['time_difference'] = {
            'seconds': time_diff,
            'human_readable': f"{abs(time_diff):.1f} seconds {'later' if time_diff > 0 else 'earlier'}"
        }

        return changes

    def _get_restore_chain(self, version: FileVersion, all_versions: List[FileVersion]) -> List[str]:
        """Get the chain of restore operations leading to this version."""
        chain = []
        current = version

        while current and current.restore_source_version:
            chain.append(current.restore_source_version)
            # Find the source version
            current = next((v for v in all_versions if v.version_id == current.restore_source_version), None)

        return chain