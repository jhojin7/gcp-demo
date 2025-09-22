# Data Model: GCP Cloud Storage Versioned File Manager

## Core Entities

### File
Represents a logical file with version history in the system.

**Fields**:
- `display_name`: User-friendly filename (e.g., "report.pdf")
- `storage_key`: Unique GCP object identifier (e.g., "user123/files/uuid-report.pdf")
- `content_type`: MIME type of the file content
- `virtual_path`: Hierarchical path for folder organization (e.g., "/documents/reports/")
- `current_version_id`: Reference to the active version
- `owner_id`: User identifier who owns the file
- `created_at`: Initial file creation timestamp
- `is_deleted`: Soft deletion flag (preserves version history)

**Validation Rules**:
- `display_name` required, max 255 chars, no path separators
- `storage_key` must be unique across bucket
- `content_type` must match file content
- `virtual_path` must start with "/" and use "/" separators
- `owner_id` required for all operations

**State Transitions**:
- Created → Active (file uploaded)
- Active → Deleted (file marked for deletion)
- Deleted → Active (file restored from version)

### FileVersion
Immutable snapshot of file content and metadata.

**Fields**:
- `version_id`: GCP generation identifier (unique per file)
- `file_storage_key`: Reference to parent file's storage key
- `size_bytes`: File content size in bytes
- `checksum`: Content hash for integrity verification
- `created_at`: Version creation timestamp
- `created_by`: User who created this version
- `operation_type`: Type of operation that created version (upload, restore, edit)
- `is_current`: Flag indicating if this is the active version
- `restore_source_version`: Reference to version used for restore operations

**Validation Rules**:
- `version_id` must be unique per file
- `size_bytes` must be positive integer
- `operation_type` must be one of: upload, restore, edit
- Only one version per file can have `is_current = true`
- `restore_source_version` required when `operation_type = restore`

**Relationships**:
- Belongs to one File
- May reference another FileVersion as restore source

### User
Entity representing file ownership and operation context.

**Fields**:
- `user_id`: Unique user identifier
- `display_name`: Human-readable user name
- `created_at`: User account creation timestamp
- `session_context`: Framework for future authentication integration

**Validation Rules**:
- `user_id` required and unique
- `display_name` required for audit trails

**Note**: Initially implemented as metadata context, prepared for future authentication system.

### Folder
Virtual container for organizing files hierarchically.

**Fields**:
- `virtual_path`: Full hierarchical path (e.g., "/documents/reports/")
- `display_name`: Folder name component (e.g., "reports")
- `parent_path`: Parent folder path (e.g., "/documents/")
- `owner_id`: User who created the folder
- `created_at`: Folder creation timestamp

**Validation Rules**:
- `virtual_path` must be unique per owner
- Path must follow Unix-style conventions
- `display_name` extracted from final path component
- Root folder "/" always exists

**Implementation Note**: Folders exist implicitly through file paths; explicit folder entities created on demand.

### Operation
Audit record for tracking user actions and system events.

**Fields**:
- `operation_id`: Unique operation identifier
- `operation_type`: Action performed (upload, download, delete, restore, view)
- `file_storage_key`: Target file reference
- `version_id`: Specific version involved (if applicable)
- `user_id`: User performing the operation
- `timestamp`: When operation occurred
- `ip_address`: Source IP for web operations
- `success`: Whether operation completed successfully
- `error_message`: Details if operation failed

**Validation Rules**:
- All operations must include `user_id` and `timestamp`
- `error_message` required when `success = false`
- `version_id` required for version-specific operations

## Entity Relationships

```
User (1) ──────── owns ──────────→ (N) File
File (1) ──────── contains ──────→ (N) FileVersion
FileVersion (0..1) ── restores ──→ (1) FileVersion
Folder (1) ────── contains ──────→ (N) File
Operation (N) ──── targets ──────→ (1) File
Operation (N) ──── performed_by ─→ (1) User
```

## Storage Implementation

### GCP Metadata Mapping
- File ownership → object metadata: `owner_id`
- Virtual folders → object metadata: `virtual_path`
- Operation context → object metadata: `operation_type`, `created_by`
- Display names → object metadata: `display_name`

### Version Management
- GCP native versioning handles FileVersion storage
- Version metadata enriched with user context
- Current version tracked through GCP object lifecycle
- Historical versions preserved with complete metadata

## Query Patterns

### File Listing
- Filter by `owner_id` and `virtual_path`
- Order by `display_name` or `created_at`
- Include current version information

### Version History
- Retrieve all versions for `storage_key`
- Order by `created_at` descending
- Include operation context and user information

### Folder Navigation
- Extract unique `virtual_path` prefixes for current level
- Filter by user ownership
- Support breadcrumb trail generation