import pytest

def test_api_files_list_success(client):
    """Test GET /api/files returns JSON list of files."""
    response = client.get('/api/files')

    # Should return 200 OK
    assert response.status_code == 200

    # Should return JSON content
    assert response.content_type == 'application/json'

    # Should contain files array and path information
    json_data = response.get_json()
    assert 'files' in json_data
    assert 'current_path' in json_data
    assert isinstance(json_data['files'], list)

def test_api_files_with_path_parameter(client):
    """Test GET /api/files with path query parameter."""
    response = client.get('/api/files?path=/documents/')

    # Should return 200 OK
    assert response.status_code == 200

    # Should return JSON with path info
    json_data = response.get_json()
    assert json_data['current_path'] == '/documents/'

def test_api_files_with_include_deleted(client):
    """Test GET /api/files with include_deleted parameter."""
    response = client.get('/api/files?include_deleted=true')

    # Should return 200 OK
    assert response.status_code == 200

    # Should return JSON
    assert response.content_type == 'application/json'

def test_api_files_default_path(client):
    """Test GET /api/files defaults to root path."""
    response = client.get('/api/files')

    # Should return 200 OK
    assert response.status_code == 200

    json_data = response.get_json()
    assert json_data['current_path'] == '/'

def test_api_files_response_schema(client):
    """Test API files response matches expected schema."""
    response = client.get('/api/files')

    if response.status_code == 200:
        json_data = response.get_json()

        # Validate top-level structure
        assert 'files' in json_data
        assert 'current_path' in json_data
        assert 'parent_path' in json_data

        # Validate file objects if any exist
        for file_obj in json_data['files']:
            required_fields = [
                'file_id', 'display_name', 'virtual_path',
                'content_type', 'size_bytes', 'modified_at',
                'owner_id', 'is_deleted'
            ]
            for field in required_fields:
                assert field in file_obj