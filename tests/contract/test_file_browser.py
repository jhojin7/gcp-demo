import pytest
from flask import url_for

def test_file_browser_main_page(client):
    """Test GET / returns file browser HTML page."""
    response = client.get('/')

    # Should return 200 OK
    assert response.status_code == 200

    # Should return HTML content
    assert response.content_type.startswith('text/html')

    # Should contain file browser elements
    assert b'file browser' in response.data.lower() or b'files' in response.data.lower()

def test_file_browser_with_path_parameter(client):
    """Test GET / with path query parameter."""
    response = client.get('/?path=/documents/')

    # Should return 200 OK
    assert response.status_code == 200

    # Should return HTML content
    assert response.content_type.startswith('text/html')

def test_file_browser_default_path(client):
    """Test GET / defaults to root path."""
    response = client.get('/')

    # Should return 200 OK
    assert response.status_code == 200

    # Should handle default path
    assert response.content_type.startswith('text/html')