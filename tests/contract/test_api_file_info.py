import pytest

def test_api_file_info_success(client):
    """Test GET /api/file/{file_id}/info returns detailed file information."""
    file_id = "test-file-id"

    response = client.get(f'/api/file/{file_id}/info')

    # Should return 200 OK
    assert response.status_code == 200

    # Should return JSON content
    assert response.content_type == 'application/json'

    # Should contain detailed file information
    json_data = response.get_json()

    # Basic file fields
    basic_fields = [
        'file_id', 'display_name', 'virtual_path',
        'content_type', 'size_bytes', 'modified_at',
        'owner_id', 'is_deleted'
    ]
    for field in basic_fields:
        assert field in json_data

    # Extended file detail fields
    detail_fields = ['created_at', 'current_version_id']
    for field in detail_fields:
        assert field in json_data

def test_api_file_info_not_found(client):
    """Test GET /api/file/{file_id}/info with invalid file returns 404."""
    file_id = "nonexistent-file"

    response = client.get(f'/api/file/{file_id}/info')

    # Should return 404 Not Found
    assert response.status_code == 404

    # Should return JSON error
    assert response.content_type == 'application/json'
    json_data = response.get_json()
    assert 'error' in json_data

def test_api_file_info_includes_metadata(client):
    """Test API file info includes storage metadata."""
    file_id = "test-file-id"

    response = client.get(f'/api/file/{file_id}/info')

    if response.status_code == 200:
        json_data = response.get_json()

        # Should include storage metadata
        assert 'storage_metadata' in json_data

        # Should have version count information
        assert 'version_count' in json_data

def test_api_file_info_response_schema(client):
    """Test API file info response matches FileDetail schema."""
    file_id = "test-file-id"

    response = client.get(f'/api/file/{file_id}/info')

    if response.status_code == 200:
        json_data = response.get_json()

        # Should be superset of File schema
        file_fields = [
            'file_id', 'display_name', 'virtual_path',
            'content_type', 'size_bytes', 'modified_at',
            'owner_id', 'is_deleted', 'version_count'
        ]
        for field in file_fields:
            assert field in json_data

        # Additional FileDetail fields
        detail_fields = [
            'created_at', 'current_version_id', 'storage_metadata'
        ]
        for field in detail_fields:
            assert field in json_data

        # Validate data types
        assert isinstance(json_data['size_bytes'], int)
        assert isinstance(json_data['is_deleted'], bool)
        assert isinstance(json_data['storage_metadata'], dict)