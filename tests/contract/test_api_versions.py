import pytest

def test_api_versions_success(client):
    """Test GET /api/versions/{file_id} returns version history JSON."""
    file_id = "test-file-id"

    response = client.get(f'/api/versions/{file_id}')

    # Should return 200 OK
    assert response.status_code == 200

    # Should return JSON content
    assert response.content_type == 'application/json'

    # Should contain file info and versions
    json_data = response.get_json()
    assert 'file_info' in json_data
    assert 'versions' in json_data
    assert isinstance(json_data['versions'], list)

def test_api_versions_file_not_found(client):
    """Test GET /api/versions/{file_id} with invalid file returns 404."""
    file_id = "nonexistent-file"

    response = client.get(f'/api/versions/{file_id}')

    # Should return 404 Not Found
    assert response.status_code == 404

    # Should return JSON error
    assert response.content_type == 'application/json'
    json_data = response.get_json()
    assert 'error' in json_data

def test_api_versions_response_schema(client):
    """Test API versions response matches expected schema."""
    file_id = "test-file-id"

    response = client.get(f'/api/versions/{file_id}')

    if response.status_code == 200:
        json_data = response.get_json()

        # Validate file_info structure
        file_info = json_data['file_info']
        file_required_fields = [
            'file_id', 'display_name', 'virtual_path',
            'content_type', 'size_bytes', 'modified_at',
            'owner_id', 'is_deleted'
        ]
        for field in file_required_fields:
            assert field in file_info

        # Validate versions structure
        for version in json_data['versions']:
            version_required_fields = [
                'version_id', 'size_bytes', 'created_at',
                'created_by', 'operation_type', 'is_current'
            ]
            for field in version_required_fields:
                assert field in version

            # Validate operation_type enum
            assert version['operation_type'] in ['upload', 'restore', 'edit']

def test_api_versions_chronological_order(client):
    """Test API versions returns versions in chronological order."""
    file_id = "test-file-id"

    response = client.get(f'/api/versions/{file_id}')

    if response.status_code == 200:
        json_data = response.get_json()
        versions = json_data['versions']

        if len(versions) > 1:
            # Should be ordered by created_at descending (newest first)
            for i in range(len(versions) - 1):
                current_time = versions[i]['created_at']
                next_time = versions[i + 1]['created_at']
                # Newer versions should come first
                assert current_time >= next_time