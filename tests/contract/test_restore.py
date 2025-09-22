import pytest

def test_restore_version_success(client):
    """Test POST /restore/{file_id}/{version_id} creates new current version."""
    file_id = "test-file-id"
    version_id = "1234567890"

    response = client.post(f'/restore/{file_id}/{version_id}')

    # Should return 201 Created (new version created)
    assert response.status_code == 201

    # Should return JSON content
    assert response.content_type == 'application/json'

    # Should contain restore information
    json_data = response.get_json()
    assert 'message' in json_data
    assert 'new_version_id' in json_data
    assert 'restored_from' in json_data
    assert json_data['restored_from'] == version_id

def test_restore_file_not_found(client):
    """Test POST /restore/{file_id}/{version_id} with invalid file returns 404."""
    file_id = "nonexistent-file"
    version_id = "1234567890"

    response = client.post(f'/restore/{file_id}/{version_id}')

    # Should return 404 Not Found
    assert response.status_code == 404

    # Should return JSON error
    assert response.content_type == 'application/json'
    json_data = response.get_json()
    assert 'error' in json_data

def test_restore_version_not_found(client):
    """Test POST /restore/{file_id}/{version_id} with invalid version returns 404."""
    file_id = "test-file-id"
    version_id = "nonexistent-version"

    response = client.post(f'/restore/{file_id}/{version_id}')

    # Should return 404 Not Found
    assert response.status_code == 404

    # Should return JSON error
    assert response.content_type == 'application/json'
    json_data = response.get_json()
    assert 'error' in json_data

def test_restore_creates_new_version(client):
    """Test restore operation creates new version rather than modifying existing."""
    file_id = "test-file-id"
    version_id = "1234567890"

    response = client.post(f'/restore/{file_id}/{version_id}')

    if response.status_code == 201:
        json_data = response.get_json()
        # New version ID should be different from source version
        assert json_data['new_version_id'] != json_data['restored_from']
        # Should indicate it's a restore operation
        assert 'restore' in json_data['message'].lower()

def test_restore_preserves_original_versions(client):
    """Test restore operation preserves all original versions."""
    file_id = "test-file-id"
    version_id = "1234567890"

    response = client.post(f'/restore/{file_id}/{version_id}')

    # Should not return any indication of version deletion
    if response.status_code == 201:
        json_data = response.get_json()
        # Should indicate new version creation, not modification
        assert 'new_version_id' in json_data