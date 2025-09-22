# Quickstart: GCP Cloud Storage Versioned File Manager

## Prerequisites
- Python 3.11+ installed
- GCP project with Cloud Storage API enabled
- Service account JSON key file
- GCP bucket with versioning enabled

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install python-dotenv
```

### 2. Configure Environment
```bash
export GCP_PROJECT_ID=your-project-id
export GCP_BUCKET_NAME=your-bucket-name
export GCP_SERVICE_ACCOUNT_KEY_PATH=/path/to/service-account-key.json
export FLASK_SECRET_KEY=your-secret-key
```

### 3. Start Application
```bash
python app.py
```

### 4. Access Web Interface
Navigate to `http://localhost:5000` in your browser.

## User Acceptance Testing

### Test Scenario 1: File Upload and Versioning
1. **Upload Initial File**
   - Navigate to file browser
   - Click "Upload File" button
   - Select a test file (e.g., `test-document.txt`)
   - Verify file appears in browser with correct name and size

2. **Create New Version**
   - Modify the same file externally
   - Upload file with same name
   - Verify new version created (file size/timestamp updated)
   - Confirm original version preserved

3. **Expected Results**
   - File browser shows updated file information
   - Version count increases
   - Both versions accessible through version history

### Test Scenario 2: Version History and Restoration
1. **View Version History**
   - Click "View Versions" for uploaded file
   - Verify chronological list of versions
   - Check relative timestamps ("X minutes ago")
   - Confirm user information displayed

2. **Restore Previous Version**
   - Select older version from history
   - Click "Restore" button
   - Verify success message displayed
   - Confirm new version created from restored content

3. **Expected Results**
   - Version history shows restore operation
   - New version marked as current
   - Original versions remain unchanged
   - File browser reflects restored content

### Test Scenario 3: File Download Operations
1. **Download Current Version**
   - From file browser, click "Download"
   - Verify correct filename in download
   - Confirm file content matches current version

2. **Download Historical Version**
   - From version history, click version-specific download
   - Verify filename includes version identifier
   - Confirm content matches historical version

3. **Expected Results**
   - Downloads complete successfully
   - Filenames distinguish between current and historical versions
   - Content integrity maintained

### Test Scenario 4: File Deletion and Recovery
1. **Delete File**
   - From file browser, click "Delete" for a file
   - Verify confirmation prompt
   - Confirm file marked as deleted
   - Check file no longer appears in main browser

2. **Access Deleted File Versions**
   - Navigate to version history for deleted file
   - Verify all versions still accessible
   - Restore version to recover file

3. **Expected Results**
   - Deleted files hidden from main view
   - Complete version history preserved
   - Restoration recovers file successfully

### Test Scenario 5: Folder Navigation
1. **Upload Files with Paths**
   - Upload files to different virtual folders:
     - `/documents/reports/report1.pdf`
     - `/documents/images/photo1.jpg`
     - `/projects/code/main.py`

2. **Navigate Folder Structure**
   - Browse folder hierarchy
   - Use breadcrumb navigation
   - Verify files organized correctly

3. **Expected Results**
   - Hierarchical folder structure displayed
   - Breadcrumb trail enables navigation
   - Files appear in correct folders

### Test Scenario 6: Error Handling
1. **Upload Oversized File**
   - Attempt to upload file exceeding size limit
   - Verify user-friendly error message
   - Confirm application remains stable

2. **Network Error Simulation**
   - Disconnect network during operation
   - Verify graceful error handling
   - Check error logging for debugging

3. **Invalid File Operations**
   - Attempt to download non-existent file
   - Try to restore invalid version
   - Verify appropriate error responses

## Performance Validation

### Response Time Tests
- File upload: Complete within 30 seconds for files under 10MB
- File browser loading: Under 2 seconds for directories with <100 files
- Version history: Load within 3 seconds for files with <50 versions
- Download initiation: Begin within 1 second

### Concurrent User Simulation
- Multiple browser sessions performing operations simultaneously
- Verify file isolation and ownership
- Confirm version integrity under concurrent modifications

## Security Validation

### File Upload Security
- Verify file type validation
- Test file size limit enforcement
- Confirm metadata sanitization

### Access Control
- Verify user context tracking
- Test file ownership isolation
- Confirm operation logging

## Cleanup Procedure
1. Remove test files from GCP bucket
2. Check application logs for errors
3. Verify no temporary files remain
4. Document any issues encountered

## Success Criteria Checklist
- [ ] All test scenarios complete successfully
- [ ] Performance targets met
- [ ] Security validations pass
- [ ] Error handling works correctly
- [ ] User interface intuitive and responsive
- [ ] Version integrity maintained throughout testing
- [ ] Application remains stable under various conditions