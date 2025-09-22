import pytest
import io

def test_version_history_and_restoration_scenario(client):
    """
    Test Scenario 2: Version History and Restoration
    1. Create multiple versions
    2. View Version History
    3. Restore Previous Version
    """
    # Step 1: Create multiple versions
    file_versions = []

    for i in range(3):
        content = f'File content version {i + 1}'.encode()
        data = {
            'file': (io.BytesIO(content), 'history-test.txt'),
            'path': '/'
        }

        upload_response = client.post('/upload', data=data, content_type='multipart/form-data')
        assert upload_response.status_code == 201

        upload_data = upload_response.get_json()
        file_versions.append({
            'version_id': upload_data['version_id'],
            'content': content
        })

    file_id = upload_data['file_id']

    # Step 2: View Version History
    # Check version history page
    history_page_response = client.get(f'/versions/{file_id}')
    assert history_page_response.status_code == 200

    page_content = history_page_response.data.decode('utf-8').lower()
    assert 'version' in page_content
    assert 'restore' in page_content

    # Check version history API
    versions_api_response = client.get(f'/api/versions/{file_id}')
    assert versions_api_response.status_code == 200

    versions_data = versions_api_response.get_json()
    versions = versions_data['versions']

    # Should have all 3 versions
    assert len(versions) >= 3

    # Should be in chronological order (newest first)
    for i in range(len(versions) - 1):
        current_time = versions[i]['created_at']
        next_time = versions[i + 1]['created_at']
        assert current_time >= next_time

    # Should have relative timestamps
    for version in versions:
        assert 'relative_time' in version

    # Should show user information
    for version in versions:
        assert 'created_by' in version

    # Step 3: Restore Previous Version
    # Get the second-to-last version (middle version)
    version_to_restore = None
    for version in versions:
        if not version['is_current']:
            version_to_restore = version
            break

    assert version_to_restore is not None
    restore_version_id = version_to_restore['version_id']

    # Perform restore
    restore_response = client.post(f'/restore/{file_id}/{restore_version_id}')
    assert restore_response.status_code == 201

    restore_data = restore_response.get_json()
    assert 'new_version_id' in restore_data
    assert 'restored_from' in restore_data
    assert restore_data['restored_from'] == restore_version_id

    new_version_id = restore_data['new_version_id']

    # Verify restoration results
    # Check updated version history
    updated_versions_response = client.get(f'/api/versions/{file_id}')
    assert updated_versions_response.status_code == 200

    updated_versions = updated_versions_response.get_json()['versions']

    # Should have one more version (restore creates new version)
    assert len(updated_versions) >= 4

    # Find the new current version
    current_version = None
    for version in updated_versions:
        if version['is_current']:
            current_version = version
            break

    assert current_version is not None
    assert current_version['version_id'] == new_version_id
    assert current_version['operation_type'] == 'restore'
    assert current_version['restore_source_version'] == restore_version_id

    # Verify file browser reflects restored content
    browser_response = client.get('/')
    assert browser_response.status_code == 200

def test_version_history_preserves_original_versions(client):
    """Test that version history preserves all original versions during restore."""
    # Create initial version
    content1 = b'Original content'
    data = {
        'file': (io.BytesIO(content1), 'preserve-test.txt'),
        'path': '/'
    }

    upload1 = client.post('/upload', data=data, content_type='multipart/form-data')
    assert upload1.status_code == 201
    file_id = upload1.get_json()['file_id']
    version1_id = upload1.get_json()['version_id']

    # Create second version
    content2 = b'Modified content'
    data['file'] = (io.BytesIO(content2), 'preserve-test.txt')
    upload2 = client.post('/upload', data=data, content_type='multipart/form-data')
    assert upload2.status_code == 201
    version2_id = upload2.get_json()['version_id']

    # Restore first version
    restore_response = client.post(f'/restore/{file_id}/{version1_id}')
    assert restore_response.status_code == 201

    # Verify all original versions still exist
    versions_response = client.get(f'/api/versions/{file_id}')
    assert versions_response.status_code == 200

    versions = versions_response.get_json()['versions']
    version_ids = [v['version_id'] for v in versions]

    # Original versions should still be present
    assert version1_id in version_ids
    assert version2_id in version_ids

    # Should have 3 versions total (original 2 + restore)
    assert len(versions) >= 3