import pytest
import io

def test_file_deletion_and_recovery_scenario(client):
    """
    Test Scenario 4: File Deletion and Recovery
    1. Delete File
    2. Access Deleted File Versions
    3. Restore file through version history
    """
    # Setup: Create file with multiple versions
    content_v1 = b'First version content'
    content_v2 = b'Second version content'
    content_v3 = b'Third version content'

    # Create multiple versions
    versions = []
    for i, content in enumerate([content_v1, content_v2, content_v3], 1):
        data = {
            'file': (io.BytesIO(content), 'deletion-test.txt'),
            'path': '/test-deletion/'
        }

        upload = client.post('/upload', data=data, content_type='multipart/form-data')
        assert upload.status_code == 201
        versions.append(upload.get_json()['version_id'])

    file_id = upload.get_json()['file_id']

    # Verify file appears in browser initially
    browser_response = client.get('/')
    assert browser_response.status_code == 200
    assert b'deletion-test.txt' in browser_response.data

    # Step 1: Delete File
    delete_response = client.post(f'/delete/{file_id}')
    assert delete_response.status_code == 200

    delete_data = delete_response.get_json()
    assert 'message' in delete_data
    assert delete_data['file_id'] == file_id

    # Verify file no longer appears in main browser view
    browser_after_delete = client.get('/')
    assert browser_after_delete.status_code == 200
    # File should be hidden from main view
    # (Implementation may still show it but marked as deleted)

    # Verify file marked as deleted in API
    files_response = client.get('/api/files')
    assert files_response.status_code == 200
    files_data = files_response.get_json()

    # File should not appear in default listing
    default_files = [f for f in files_data['files'] if f['display_name'] == 'deletion-test.txt']
    if default_files:
        # If shown, should be marked as deleted
        assert default_files[0]['is_deleted'] is True

    # Step 2: Access Deleted File Versions
    # Version history should still be accessible
    versions_response = client.get(f'/versions/{file_id}')
    assert versions_response.status_code == 200

    versions_api_response = client.get(f'/api/versions/{file_id}')
    assert versions_api_response.status_code == 200

    versions_data = versions_api_response.get_json()
    all_versions = versions_data['versions']

    # All versions should still be accessible
    assert len(all_versions) >= 3

    # All original versions should be preserved
    original_version_ids = set(versions)
    found_version_ids = {v['version_id'] for v in all_versions}
    assert original_version_ids.issubset(found_version_ids)

    # Step 3: Restore file through version history
    # Restore from a previous version
    version_to_restore = versions[1]  # Second version

    restore_response = client.post(f'/restore/{file_id}/{version_to_restore}')
    assert restore_response.status_code == 201

    restore_data = restore_response.get_json()
    assert 'new_version_id' in restore_data
    assert restore_data['restored_from'] == version_to_restore

    # Verify file recovery
    # File should appear in browser again
    browser_after_restore = client.get('/')
    assert browser_after_restore.status_code == 200
    assert b'deletion-test.txt' in browser_after_restore.data

    # File should be marked as not deleted in API
    files_after_restore = client.get('/api/files')
    assert files_after_restore.status_code == 200
    files_after_restore_data = files_after_restore.get_json()

    restored_file = None
    for f in files_after_restore_data['files']:
        if f['display_name'] == 'deletion-test.txt':
            restored_file = f
            break

    assert restored_file is not None
    assert restored_file['is_deleted'] is False

def test_deleted_files_with_include_deleted_parameter(client):
    """Test that deleted files can be accessed with include_deleted parameter."""
    # Create and delete a file
    content = b'Content for include_deleted test'
    data = {
        'file': (io.BytesIO(content), 'include-deleted-test.txt'),
        'path': '/'
    }

    upload = client.post('/upload', data=data, content_type='multipart/form-data')
    assert upload.status_code == 201
    file_id = upload.get_json()['file_id']

    # Delete the file
    delete_response = client.post(f'/delete/{file_id}')
    assert delete_response.status_code == 200

    # Check that file doesn't appear in default listing
    default_files = client.get('/api/files')
    assert default_files.status_code == 200
    default_data = default_files.get_json()

    default_file_names = [f['display_name'] for f in default_data['files']]
    # Should not include deleted file or should mark it as deleted
    deleted_files_in_default = [f for f in default_data['files']
                               if f['display_name'] == 'include-deleted-test.txt' and not f['is_deleted']]
    assert len(deleted_files_in_default) == 0

    # Check that file appears with include_deleted=true
    with_deleted_files = client.get('/api/files?include_deleted=true')
    assert with_deleted_files.status_code == 200
    with_deleted_data = with_deleted_files.get_json()

    deleted_file = None
    for f in with_deleted_data['files']:
        if f['display_name'] == 'include-deleted-test.txt':
            deleted_file = f
            break

    assert deleted_file is not None
    assert deleted_file['is_deleted'] is True

def test_deletion_preserves_all_version_history(client):
    """Test that deletion preserves complete version history."""
    # Create file with multiple versions
    versions_data = []
    for i in range(5):
        content = f'Version {i + 1} content'.encode()
        data = {
            'file': (io.BytesIO(content), 'history-preservation-test.txt'),
            'path': '/'
        }

        upload = client.post('/upload', data=data, content_type='multipart/form-data')
        assert upload.status_code == 201
        versions_data.append({
            'version_id': upload.get_json()['version_id'],
            'content': content
        })

    file_id = upload.get_json()['file_id']

    # Get version history before deletion
    before_delete = client.get(f'/api/versions/{file_id}')
    assert before_delete.status_code == 200
    versions_before = before_delete.get_json()['versions']
    version_ids_before = {v['version_id'] for v in versions_before}

    # Delete file
    delete_response = client.post(f'/delete/{file_id}')
    assert delete_response.status_code == 200

    # Get version history after deletion
    after_delete = client.get(f'/api/versions/{file_id}')
    assert after_delete.status_code == 200
    versions_after = after_delete.get_json()['versions']
    version_ids_after = {v['version_id'] for v in versions_after}

    # All versions should still be present
    assert version_ids_before == version_ids_after
    assert len(versions_after) >= 5

    # All versions should still be downloadable
    for version_data in versions_data:
        version_id = version_data['version_id']
        expected_content = version_data['content']

        download = client.get(f'/download/{file_id}/{version_id}')
        assert download.status_code == 200
        assert download.data == expected_content