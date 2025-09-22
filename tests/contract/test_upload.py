import pytest
import io

def test_upload_file_success(client):
    """Test POST /upload with valid file returns 201 with JSON response."""
    data = {
        'file': (io.BytesIO(b'test file content'), 'test.txt'),
        'path': '/'
    }

    response = client.post('/upload', data=data, content_type='multipart/form-data')

    # Should return 201 Created
    assert response.status_code == 201

    # Should return JSON content
    assert response.content_type == 'application/json'

    # Should contain required response fields
    json_data = response.get_json()
    assert 'message' in json_data
    assert 'file_id' in json_data
    assert 'version_id' in json_data

def test_upload_file_missing_file(client):
    """Test POST /upload without file returns 400 error."""
    data = {'path': '/'}

    response = client.post('/upload', data=data, content_type='multipart/form-data')

    # Should return 400 Bad Request
    assert response.status_code == 400

    # Should return JSON error
    assert response.content_type == 'application/json'
    json_data = response.get_json()
    assert 'error' in json_data

def test_upload_file_with_virtual_path(client):
    """Test POST /upload with custom virtual path."""
    data = {
        'file': (io.BytesIO(b'test content'), 'test.txt'),
        'path': '/documents/reports/'
    }

    response = client.post('/upload', data=data, content_type='multipart/form-data')

    # Should return 201 Created
    assert response.status_code == 201

    # Should return JSON response
    assert response.content_type == 'application/json'

def test_upload_file_creates_new_version(client):
    """Test POST /upload with same filename creates new version."""
    data = {
        'file': (io.BytesIO(b'original content'), 'test.txt'),
        'path': '/'
    }

    # First upload
    response1 = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response1.status_code == 201

    # Second upload with same name
    data['file'] = (io.BytesIO(b'updated content'), 'test.txt')
    response2 = client.post('/upload', data=data, content_type='multipart/form-data')
    assert response2.status_code == 201

    # Should return different version IDs
    json1 = response1.get_json()
    json2 = response2.get_json()
    assert json1['version_id'] != json2['version_id']