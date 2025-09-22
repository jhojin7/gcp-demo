# GCP Cloud Storage Versioned File Manager - Project Specification

## Project Overview

Build a web application demonstrating Google Cloud Platform Cloud Storage versioned file capabilities with basic CRUD operations. The system should implement Time Machine-style file versioning with a Flask backend and minimal HTML/CSS/JS frontend.

## Architecture Requirements

### Backend Framework
- Use Flask as the web framework
- Implement clean code principles with separation of concerns
- Create modular components for different functionalities
- Use service layer pattern for GCP interactions

### Frontend
- Simple text-based browser UI using HTML, CSS, and JavaScript
- No complex frameworks required
- Responsive design not required for initial version
- Focus on functionality over aesthetics

## Technical Stack

### Required Dependencies
- Flask for web framework
- Google Cloud Storage Python client library
- Python datetime utilities for relative time formatting
- Standard Python libraries for file handling

### File Structure
```
project-root/
├── app.py                 # Main Flask application
├── gcp_storage.py         # GCP Storage service layer
├── config.py             # Application configuration
├── requirements.txt      # Python dependencies
├── templates/
│   ├── index.html        # File browser page
│   ├── versions.html     # Version history page
│   └── base.html         # Base template
└── static/
    ├── style.css         # Basic styling
    └── script.js         # Frontend interactions
```

## Authentication & User Management

### Current Implementation
- Build with multi-user architecture but implement single-user functionality initially
- Include user identification in all file operations through metadata
- Prepare structure for future simple ID/password authentication system
- Use clean separation to allow easy auth layer addition later

### Future Expansion Readiness
- Design file ownership tracking system
- Create user context handling in service layer
- Implement session management foundation

## File Operations & CRUD

### Upload Functionality
- Accept files through web form upload
- Store user ownership information in GCP object metadata
- Support recursive directory structure
- Generate unique object names to prevent conflicts while maintaining user-friendly display names

### Download Functionality
- Allow downloading current version of any file
- Support downloading specific historical versions
- Maintain original filenames for downloads

### Delete Operations
- Delete operations should NOT remove file versions
- Mark files as deleted while preserving version history
- Allow restoration of deleted files through version history

### List Operations
- Display all files in hierarchical folder structure
- Show file metadata including owner, size, last modified
- Support navigation through directory levels
- Filter files by current user ownership

## Versioning System

### Version Storage
- Leverage GCP Cloud Storage native versioning
- Each file modification creates new version automatically
- Store user information and operation type in version metadata
- Track version creation reasons (upload, restore, edit)

### Time Machine-Style Restore
- Restoring previous version creates NEW current version
- Original historical versions remain unchanged
- New version includes metadata indicating it's a restore operation
- Maintain complete audit trail of all operations

### Version Display
- Show relative timestamps: "2 minutes ago", "1 hour ago", "Yesterday", "Last week", "3 months ago"
- Display version size and user who created each version
- Order versions chronologically with newest first
- Include restoration chain information when applicable

## User Interface Requirements

### File Browser Page (Main)
- Display files and folders in table format
- Columns: Name, Size, Modified Date, Owner, Actions
- Actions include: Download, Delete, View Versions
- Support folder navigation with breadcrumb trail
- Include upload form for new files

### Version History Page
- Dedicated page for viewing file version history
- Table format showing: Version Date, Size, User, Action Type, Restore Option
- Restore button for each historical version
- Back navigation to file browser
- Clear indication of current active version

### Navigation Flow
- Main page shows file browser
- Click "View Versions" opens version history page for specific file
- Version history page includes restore functionality
- All operations redirect appropriately with success/error messages

## GCP Integration Specifications

### Authentication
- Use service account JSON key file for GCP authentication
- Load key file path from configuration
- Handle authentication errors gracefully

### Bucket Configuration
- Use single shared bucket for all users and files
- Implement flat storage with metadata-based organization
- Enable versioning on the bucket
- Configure appropriate bucket permissions

### Metadata Management
- Store user ownership in object metadata
- Include operation timestamps and types
- Track file display names vs storage names
- Maintain directory structure information in metadata

## API Endpoints Design

### File Management Endpoints
- GET / - File browser main page
- POST /upload - Handle file uploads
- GET /download/<file_id> - Download current file version
- GET /download/<file_id>/<version_id> - Download specific version
- POST /delete/<file_id> - Mark file as deleted
- GET /versions/<file_id> - Version history page
- POST /restore/<file_id>/<version_id> - Restore specific version

### Data Endpoints
- GET /api/files - JSON list of files for current user
- GET /api/versions/<file_id> - JSON version history for file
- GET /api/file/<file_id>/info - File metadata and information

## Configuration Management

### Application Settings
- GCP service account key file path
- GCP project ID and bucket name
- Application secret key for sessions
- Debug mode configuration
- File size limits and allowed types

### Environment Variables
- Support configuration through environment variables
- Provide sensible defaults where applicable
- Clear documentation of required vs optional settings

## Error Handling Requirements

### GCP Error Management
- Handle authentication failures
- Manage network connectivity issues
- Process quota exceeded situations
- Deal with file not found scenarios

### User Error Handling
- Validate file uploads (size, type, permissions)
- Handle duplicate file name scenarios
- Manage version not found situations
- Process malformed requests gracefully

### Error Display
- Show user-friendly error messages
- Log detailed errors for debugging
- Provide clear next steps for recoverable errors
- Maintain application stability during errors

## Success Criteria

### Functional Requirements
- Successfully upload files with automatic versioning
- Browse files in organized directory structure
- View complete version history for any file
- Restore previous versions creating new current version
- Download any version of any file
- Mark files as deleted while preserving versions

### Technical Requirements
- Clean, maintainable code structure
- Proper separation of concerns
- Robust error handling
- Efficient GCP API usage
- Responsive user interface operations

### User Experience Requirements
- Intuitive navigation between file browser and version history
- Clear visual indication of file states and operations
- Meaningful timestamps and version information
- Successful operation feedback
- Clear error messages when issues occur

## Future Enhancement Readiness

### Authentication System
- Code structure ready for login/logout functionality
- User session management foundation in place
- Permission checking framework prepared

### Advanced Features
- File sharing capabilities foundation
- Search and filter functionality structure
- Bulk operations support framework
- Advanced metadata and tagging system preparation
