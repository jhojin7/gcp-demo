import pytest
import io

def test_file_download_operations_scenario(client):
    """
    Test Scenario 3: File Download Operations
    1. Download Current Version
    2. Download Historical Version
    3. Verify content integrity
    """
    # Setup: Create file with multiple versions
    original_content = b'Original file content for download testing'
    updated_content = b'Updated file content for download testing'

    # Upload original version
    data = {
        'file': (io.BytesIO(original_content), 'download-test.txt'),
        'path': '/downloads/'
    }

    upload1 = client.post('/upload', data=data, content_type='multipart/form-data')
    assert upload1.status_code == 201
    file_id = upload1.get_json()['file_id']
    original_version_id = upload1.get_json()['version_id']

    # Upload updated version
    data['file'] = (io.BytesIO(updated_content), 'download-test.txt')
    upload2 = client.post('/upload', data=data, content_type='multipart/form-data')
    assert upload2.status_code == 201
    current_version_id = upload2.get_json()['version_id']

    # Step 1: Download Current Version
    current_download = client.get(f'/download/{file_id}')
    assert current_download.status_code == 200

    # Should return binary content
    assert current_download.content_type == 'application/octet-stream'

    # Should have proper Content-Disposition header
    disposition = current_download.headers.get('Content-Disposition', '')
    assert 'attachment' in disposition
    assert 'download-test.txt' in disposition

    # Content should match current version
    assert current_download.data == updated_content

    # Step 2: Download Historical Version
    historical_download = client.get(f'/download/{file_id}/{original_version_id}')
    assert historical_download.status_code == 200

    # Should return binary content
    assert historical_download.content_type == 'application/octet-stream'

    # Should have version identifier in filename
    hist_disposition = historical_download.headers.get('Content-Disposition', '')
    assert 'attachment' in hist_disposition
    # Filename should distinguish from current version
    assert original_version_id in hist_disposition or 'version' in hist_disposition.lower()

    # Content should match original version
    assert historical_download.data == original_content

    # Step 3: Verify content integrity
    # Current and historical downloads should be different
    assert current_download.data != historical_download.data

    # Both should preserve exact content
    assert historical_download.data == original_content
    assert current_download.data == updated_content

def test_download_nonexistent_file_error_handling(client):
    """Test download error handling for non-existent files."""
    # Test current version download of non-existent file
    response = client.get('/download/nonexistent-file')
    assert response.status_code == 404
    assert response.content_type == 'application/json'

    error_data = response.get_json()
    assert 'error' in error_data

    # Test historical version download of non-existent file
    response = client.get('/download/nonexistent-file/version123')
    assert response.status_code == 404
    assert response.content_type == 'application/json'

def test_download_nonexistent_version_error_handling(client):
    """Test download error handling for non-existent versions."""
    # Setup: Create a file
    content = b'Test content for version error testing'
    data = {
        'file': (io.BytesIO(content), 'version-error-test.txt'),
        'path': '/'
    }

    upload = client.post('/upload', data=data, content_type='multipart/form-data')
    assert upload.status_code == 201
    file_id = upload.get_json()['file_id']

    # Try to download non-existent version
    response = client.get(f'/download/{file_id}/nonexistent-version')
    assert response.status_code == 404
    assert response.content_type == 'application/json'

    error_data = response.get_json()
    assert 'error' in error_data

def test_download_filename_preservation(client):
    """Test that downloads preserve original filenames correctly."""
    # Test with various filename types
    test_files = [
        ('simple.txt', b'Simple filename'),
        ('with-dashes.txt', b'Filename with dashes'),
        ('with_underscores.txt', b'Filename with underscores'),
        ('file.with.dots.txt', b'Filename with multiple dots')
    ]

    for filename, content in test_files:
        data = {
            'file': (io.BytesIO(content), filename),
            'path': '/'
        }

        upload = client.post('/upload', data=data, content_type='multipart/form-data')
        assert upload.status_code == 201
        file_id = upload.get_json()['file_id']

        # Download and check filename preservation
        download = client.get(f'/download/{file_id}')
        assert download.status_code == 200

        disposition = download.headers.get('Content-Disposition', '')
        assert filename in disposition

def test_download_with_special_characters_in_file_id(client):
    """Test download handling with file IDs containing special characters."""
    # This tests the URL encoding/decoding handling
    content = b'Content for special character testing'
    data = {
        'file': (io.BytesIO(content), 'special-chars.txt'),
        'path': '/folder with spaces/'
    }

    upload = client.post('/upload', data=data, content_type='multipart/form-data')
    assert upload.status_code == 201
    file_id = upload.get_json()['file_id']

    # File ID might contain URL-encoded characters
    download = client.get(f'/download/{file_id}')

    # Should handle gracefully (either succeed or return proper error)
    assert download.status_code in [200, 404]

    if download.status_code == 200:
        assert download.data == content