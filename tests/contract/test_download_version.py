import pytest

def test_download_specific_version_success(client):
    """Test GET /download/{file_id}/{version_id} returns specific version content."""
    file_id = "test-file-id"
    version_id = "1234567890"

    response = client.get(f'/download/{file_id}/{version_id}')

    # Should return 200 OK when version exists
    assert response.status_code == 200

    # Should return binary content
    assert response.content_type == 'application/octet-stream'

    # Should include version info in filename
    disposition = response.headers.get('Content-Disposition', '')
    assert 'attachment' in disposition
    assert 'filename=' in disposition

def test_download_version_not_found(client):
    """Test GET /download/{file_id}/{version_id} with invalid version returns 404."""
    file_id = "test-file-id"
    version_id = "invalid-version"

    response = client.get(f'/download/{file_id}/{version_id}')

    # Should return 404 Not Found
    assert response.status_code == 404

    # Should return JSON error
    assert response.content_type == 'application/json'
    json_data = response.get_json()
    assert 'error' in json_data

def test_download_version_file_not_found(client):
    """Test GET /download/{file_id}/{version_id} with invalid file returns 404."""
    file_id = "nonexistent-file"
    version_id = "1234567890"

    response = client.get(f'/download/{file_id}/{version_id}')

    # Should return 404 Not Found
    assert response.status_code == 404

    # Should return JSON error
    assert response.content_type == 'application/json'
    json_data = response.get_json()
    assert 'error' in json_data

def test_download_version_filename_includes_version(client):
    """Test download version response includes version identifier in filename."""
    file_id = "test-file-id"
    version_id = "1234567890"

    response = client.get(f'/download/{file_id}/{version_id}')

    if response.status_code == 200:
        # Should include version info to distinguish from current version
        disposition = response.headers.get('Content-Disposition', '')
        assert version_id in disposition or 'version' in disposition.lower()