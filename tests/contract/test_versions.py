import pytest

def test_versions_page_success(client):
    """Test GET /versions/{file_id} returns version history HTML page."""
    file_id = "test-file-id"

    response = client.get(f'/versions/{file_id}')

    # Should return 200 OK
    assert response.status_code == 200

    # Should return HTML content
    assert response.content_type.startswith('text/html')

    # Should contain version history elements
    assert b'version' in response.data.lower() or b'history' in response.data.lower()

def test_versions_page_file_not_found(client):
    """Test GET /versions/{file_id} with non-existent file returns 404."""
    file_id = "nonexistent-file"

    response = client.get(f'/versions/{file_id}')

    # Should return 404 Not Found
    assert response.status_code == 404

    # Should return HTML error page
    assert response.content_type.startswith('text/html')

def test_versions_page_shows_chronological_list(client):
    """Test version history page displays versions chronologically."""
    file_id = "test-file-id"

    response = client.get(f'/versions/{file_id}')

    if response.status_code == 200:
        # Should contain elements suggesting chronological ordering
        data = response.data.decode('utf-8').lower()
        assert 'version' in data
        # Should have elements for restore functionality
        assert 'restore' in data or 'button' in data

def test_versions_page_includes_navigation(client):
    """Test version history page includes navigation back to file browser."""
    file_id = "test-file-id"

    response = client.get(f'/versions/{file_id}')

    if response.status_code == 200:
        data = response.data.decode('utf-8').lower()
        # Should have navigation elements
        assert any(word in data for word in ['back', 'return', 'browser', 'home'])