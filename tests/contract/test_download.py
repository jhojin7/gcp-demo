import pytest

def test_download_current_file_success(client):
    """Test GET /download/{file_id} returns file content with proper headers."""
    file_id = "test-file-id"

    response = client.get(f'/download/{file_id}')

    # Should return 200 OK (when file exists)
    # This will initially fail until implementation exists
    assert response.status_code == 200

    # Should return binary content
    assert response.content_type == 'application/octet-stream'

    # Should have Content-Disposition header with filename
    assert 'Content-Disposition' in response.headers
    assert 'attachment' in response.headers['Content-Disposition']

def test_download_nonexistent_file(client):
    """Test GET /download/{file_id} with non-existent file returns 404."""
    file_id = "nonexistent-file"

    response = client.get(f'/download/{file_id}')

    # Should return 404 Not Found
    assert response.status_code == 404

    # Should return JSON error
    assert response.content_type == 'application/json'
    json_data = response.get_json()
    assert 'error' in json_data

def test_download_file_with_special_characters(client):
    """Test download with file ID containing special characters."""
    file_id = "user123/files/test-file.txt"

    response = client.get(f'/download/{file_id}')

    # Should handle special characters in file ID
    # Will return 404 until implementation, but should not crash
    assert response.status_code in [200, 404]

def test_download_preserves_original_filename(client):
    """Test download response includes original filename."""
    file_id = "test-file-id"

    response = client.get(f'/download/{file_id}')

    if response.status_code == 200:
        # Should preserve original filename in Content-Disposition
        disposition = response.headers.get('Content-Disposition', '')
        assert 'filename=' in disposition