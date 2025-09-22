import pytest
import io

def test_file_upload_and_versioning_scenario(client):
    """
    Test Scenario 1: File Upload and Versioning
    1. Upload Initial File
    2. Create New Version
    3. Verify version tracking
    """
    # Step 1: Upload Initial File
    initial_content = b'Initial file content for testing'
    data = {
        'file': (io.BytesIO(initial_content), 'test-document.txt'),
        'path': '/'
    }

    upload_response = client.post('/upload', data=data, content_type='multipart/form-data')

    # Should successfully upload
    assert upload_response.status_code == 201
    upload_data = upload_response.get_json()
    file_id = upload_data['file_id']
    first_version_id = upload_data['version_id']

    # Verify file appears in browser
    browser_response = client.get('/')
    assert browser_response.status_code == 200
    assert b'test-document.txt' in browser_response.data

    # Step 2: Create New Version (same filename, different content)
    updated_content = b'Updated file content with new information'
    data['file'] = (io.BytesIO(updated_content), 'test-document.txt')

    second_upload_response = client.post('/upload', data=data, content_type='multipart/form-data')

    # Should create new version
    assert second_upload_response.status_code == 201
    second_upload_data = second_upload_response.get_json()
    second_version_id = second_upload_data['version_id']

    # Should have different version IDs
    assert first_version_id != second_version_id
    assert second_upload_data['file_id'] == file_id  # Same file

    # Step 3: Verify version tracking
    # Check file listing API shows updated information
    files_response = client.get('/api/files')
    assert files_response.status_code == 200
    files_data = files_response.get_json()

    # Find our test file
    test_file = None
    for file_obj in files_data['files']:
        if file_obj['display_name'] == 'test-document.txt':
            test_file = file_obj
            break

    assert test_file is not None
    # Should show increased version count
    assert test_file['version_count'] >= 2

    # Check version history API
    versions_response = client.get(f'/api/versions/{file_id}')
    assert versions_response.status_code == 200
    versions_data = versions_response.get_json()

    # Should have both versions accessible
    versions = versions_data['versions']
    assert len(versions) >= 2

    # Should have one current version
    current_versions = [v for v in versions if v['is_current']]
    assert len(current_versions) == 1

    # Current version should be the latest
    current_version = current_versions[0]
    assert current_version['version_id'] == second_version_id

def test_version_metadata_tracking(client):
    """Test that version metadata includes user and operation information."""
    content = b'Test content for metadata tracking'
    data = {
        'file': (io.BytesIO(content), 'metadata-test.txt'),
        'path': '/documents/'
    }

    upload_response = client.post('/upload', data=data, content_type='multipart/form-data')
    assert upload_response.status_code == 201

    file_id = upload_response.get_json()['file_id']

    # Check version metadata
    versions_response = client.get(f'/api/versions/{file_id}')
    assert versions_response.status_code == 200

    versions = versions_response.get_json()['versions']
    assert len(versions) >= 1

    version = versions[0]
    # Should track operation type
    assert version['operation_type'] == 'upload'
    # Should track user information
    assert 'created_by' in version
    # Should have timestamp
    assert 'created_at' in version