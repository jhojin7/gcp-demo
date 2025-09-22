from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import os


@dataclass
class Folder:
    """
    Virtual container for organizing files hierarchically.
    """
    virtual_path: str
    owner_id: str
    display_name: Optional[str] = None
    parent_path: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate folder data after initialization."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()

        # Extract display name from path if not provided
        if self.display_name is None:
            self.display_name = self._extract_display_name()

        # Calculate parent path if not provided
        if self.parent_path is None:
            self.parent_path = self._calculate_parent_path()

        self.validate()

    def _extract_display_name(self) -> str:
        """Extract folder name from virtual path."""
        # Remove trailing slash for processing
        path = self.virtual_path.rstrip('/')

        # Root folder
        if path == '' or path == '/':
            return 'Root'

        # Extract last component
        return os.path.basename(path)

    def _calculate_parent_path(self) -> str:
        """Calculate parent folder path."""
        # Root folder has no parent
        if self.virtual_path == '/':
            return '/'

        # Remove trailing slash for processing
        path = self.virtual_path.rstrip('/')

        # Get parent directory
        parent = os.path.dirname(path)

        # Ensure parent ends with slash
        if not parent.endswith('/'):
            parent += '/'

        return parent

    def validate(self):
        """Validate folder fields according to business rules."""
        # Virtual path validation
        if not self.virtual_path:
            raise ValueError("Virtual path is required")

        # Must follow Unix-style conventions
        if not self.virtual_path.startswith('/'):
            raise ValueError("Virtual path must start with '/'")

        if not self.virtual_path.endswith('/'):
            raise ValueError("Virtual path must end with '/'")

        # No double slashes except for root
        if '//' in self.virtual_path and self.virtual_path != '//':
            raise ValueError("Virtual path cannot contain double slashes")

        # Owner ID validation
        if not self.owner_id:
            raise ValueError("Owner ID is required")

        # Display name validation
        if not self.display_name:
            raise ValueError("Display name cannot be empty")

    def get_full_path(self) -> str:
        """Get the full virtual path."""
        return self.virtual_path

    def get_breadcrumb_trail(self) -> List[dict]:
        """Generate breadcrumb trail for navigation."""
        breadcrumbs = []

        # Always start with root
        breadcrumbs.append({
            'name': 'Root',
            'path': '/',
            'is_current': self.virtual_path == '/'
        })

        # If not root, add intermediate folders
        if self.virtual_path != '/':
            path_parts = self.virtual_path.strip('/').split('/')
            current_path = '/'

            for i, part in enumerate(path_parts):
                if part:  # Skip empty parts
                    current_path += part + '/'
                    breadcrumbs.append({
                        'name': part,
                        'path': current_path,
                        'is_current': current_path == self.virtual_path
                    })

        return breadcrumbs

    def get_child_path(self, child_name: str) -> str:
        """Get path for a child folder."""
        if not child_name:
            raise ValueError("Child name cannot be empty")

        # Ensure child name doesn't contain path separators
        if '/' in child_name or '\\' in child_name:
            raise ValueError("Child name cannot contain path separators")

        return f"{self.virtual_path}{child_name}/"

    def is_root(self) -> bool:
        """Check if this is the root folder."""
        return self.virtual_path == '/'

    def is_parent_of(self, other_path: str) -> bool:
        """Check if this folder is a parent of the given path."""
        if not other_path:
            return False

        # Normalize paths
        my_path = self.virtual_path.rstrip('/') + '/'
        test_path = other_path.rstrip('/') + '/'

        return test_path.startswith(my_path) and test_path != my_path

    def is_child_of(self, parent_path: str) -> bool:
        """Check if this folder is a child of the given path."""
        if not parent_path:
            return False

        # Normalize paths
        test_parent = parent_path.rstrip('/') + '/'
        my_path = self.virtual_path.rstrip('/') + '/'

        return my_path.startswith(test_parent) and my_path != test_parent

    def get_depth(self) -> int:
        """Get the depth level of this folder (root = 0)."""
        if self.virtual_path == '/':
            return 0

        # Count directory separators minus 1 (for trailing slash)
        return self.virtual_path.count('/') - 1

    def to_dict(self) -> dict:
        """Convert folder to dictionary representation."""
        return {
            'virtual_path': self.virtual_path,
            'display_name': self.display_name,
            'parent_path': self.parent_path,
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_root': self.is_root(),
            'depth': self.get_depth(),
            'breadcrumbs': self.get_breadcrumb_trail()
        }

    @classmethod
    def create_from_file_path(cls, file_virtual_path: str, owner_id: str) -> 'Folder':
        """Create folder instance from a file's virtual path."""
        # Extract directory path from file path
        folder_path = os.path.dirname(file_virtual_path)

        # Ensure it ends with slash
        if not folder_path.endswith('/'):
            folder_path += '/'

        return cls(
            virtual_path=folder_path,
            owner_id=owner_id
        )

    @classmethod
    def create_root_folder(cls, owner_id: str) -> 'Folder':
        """Create root folder instance."""
        return cls(
            virtual_path='/',
            owner_id=owner_id
        )

    def __str__(self) -> str:
        """String representation of folder."""
        return f"Folder({self.display_name} -> {self.virtual_path})"

    def __eq__(self, other) -> bool:
        """Check equality based on virtual path and owner."""
        if not isinstance(other, Folder):
            return False
        return self.virtual_path == other.virtual_path and self.owner_id == other.owner_id

    def __lt__(self, other) -> bool:
        """Enable sorting by virtual path."""
        if not isinstance(other, Folder):
            return NotImplemented
        return self.virtual_path < other.virtual_path