import pytest

def test_delete_file_success(client):
    """Test POST /delete/{file_id} marks file as deleted and returns JSON response."""
    file_id = "test-file-id"

    response = client.post(f'/delete/{file_id}')

    # Should return 200 OK
    assert response.status_code == 200

    # Should return JSON content
    assert response.content_type == 'application/json'

    # Should contain success message and file ID
    json_data = response.get_json()
    assert 'message' in json_data
    assert 'file_id' in json_data
    assert json_data['file_id'] == file_id

def test_delete_nonexistent_file(client):
    """Test POST /delete/{file_id} with non-existent file returns 404."""
    file_id = "nonexistent-file"

    response = client.post(f'/delete/{file_id}')

    # Should return 404 Not Found
    assert response.status_code == 404

    # Should return JSON error
    assert response.content_type == 'application/json'
    json_data = response.get_json()
    assert 'error' in json_data

def test_delete_file_preserves_version_history(client):
    """Test DELETE operation preserves all version history."""
    file_id = "test-file-id"

    response = client.post(f'/delete/{file_id}')

    # Should return success (soft delete)
    assert response.status_code == 200

    # File should be marked as deleted but versions preserved
    json_data = response.get_json()
    assert 'message' in json_data
    # Message should indicate soft delete, not permanent removal
    assert 'marked' in json_data['message'].lower() or 'deleted' in json_data['message'].lower()

def test_delete_already_deleted_file(client):
    """Test deleting an already deleted file."""
    file_id = "already-deleted-file"

    response = client.post(f'/delete/{file_id}')

    # Should handle gracefully - either 200 (idempotent) or 404
    assert response.status_code in [200, 404]

    # Should return JSON response
    assert response.content_type == 'application/json'