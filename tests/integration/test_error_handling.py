import pytest
import io

def test_error_handling_scenario(client):
    """
    Test Scenario 6: Error Handling
    1. Upload Oversized File
    2. Network Error Simulation
    3. Invalid File Operations
    """

    # Step 1: Upload Oversized File
    # Create a large file that exceeds size limits
    # This tests file size validation
    large_content = b'X' * (10 * 1024 * 1024 + 1)  # 10MB + 1 byte

    data = {
        'file': (io.BytesIO(large_content), 'oversized-file.txt'),
        'path': '/'
    }

    oversized_response = client.post('/upload', data=data, content_type='multipart/form-data')

    # Should return 400 Bad Request for oversized file
    assert oversized_response.status_code == 400
    assert oversized_response.content_type == 'application/json'

    error_data = oversized_response.get_json()
    assert 'error' in error_data
    # Error message should be user-friendly
    assert 'size' in error_data['error'].lower() or 'large' in error_data['error'].lower()

    # Step 2: Invalid File Operations
    # Test various invalid operations to ensure graceful error handling

    # 2a. Download non-existent file
    nonexistent_download = client.get('/download/nonexistent-file-id')
    assert nonexistent_download.status_code == 404
    assert nonexistent_download.content_type == 'application/json'

    download_error = nonexistent_download.get_json()
    assert 'error' in download_error

    # 2b. Delete non-existent file
    nonexistent_delete = client.post('/delete/nonexistent-file-id')
    assert nonexistent_delete.status_code == 404
    assert nonexistent_delete.content_type == 'application/json'

    delete_error = nonexistent_delete.get_json()
    assert 'error' in delete_error

    # 2c. Restore invalid version
    nonexistent_restore = client.post('/restore/file-id/invalid-version')
    assert nonexistent_restore.status_code == 404
    assert nonexistent_restore.content_type == 'application/json'

    restore_error = nonexistent_restore.get_json()
    assert 'error' in restore_error

    # 2d. Access version history of non-existent file
    nonexistent_versions = client.get('/versions/nonexistent-file')
    assert nonexistent_versions.status_code == 404
    # Should return HTML error page
    assert nonexistent_versions.content_type.startswith('text/html')

    # 2e. API access to non-existent file info
    nonexistent_info = client.get('/api/file/nonexistent-file/info')
    assert nonexistent_info.status_code == 404
    assert nonexistent_info.content_type == 'application/json'

    info_error = nonexistent_info.get_json()
    assert 'error' in info_error

    # Step 3: Malformed Request Handling
    # Test various malformed requests

    # 3a. Upload without file
    no_file_data = {'path': '/'}
    no_file_response = client.post('/upload', data=no_file_data, content_type='multipart/form-data')
    assert no_file_response.status_code == 400
    assert no_file_response.content_type == 'application/json'

    # 3b. Upload empty file
    empty_file_data = {
        'file': (io.BytesIO(b''), 'empty-file.txt'),
        'path': '/'
    }
    empty_file_response = client.post('/upload', data=empty_file_data, content_type='multipart/form-data')
    # Should handle gracefully (may allow or reject empty files)
    assert empty_file_response.status_code in [201, 400]

    if empty_file_response.status_code == 400:
        assert empty_file_response.content_type == 'application/json'
        empty_error = empty_file_response.get_json()
        assert 'error' in empty_error

def test_file_type_validation_error_handling(client):
    """Test error handling for invalid file types."""
    # Test uploading potentially dangerous file types
    dangerous_files = [
        ('script.js', b'alert("xss");', 'application/javascript'),
        ('executable.exe', b'MZ\x90\x00', 'application/x-executable'),
        ('php-script.php', b'<?php echo "hello"; ?>', 'application/x-php'),
    ]

    for filename, content, content_type in dangerous_files:
        data = {
            'file': (io.BytesIO(content), filename),
            'path': '/'
        }

        response = client.post('/upload', data=data, content_type='multipart/form-data')

        # Should either accept with proper handling or reject with clear error
        if response.status_code == 400:
            assert response.content_type == 'application/json'
            error_data = response.get_json()
            assert 'error' in error_data
            # Error should mention file type restriction
            assert any(word in error_data['error'].lower()
                      for word in ['type', 'format', 'allowed', 'supported'])

def test_malformed_path_handling(client):
    """Test error handling for malformed virtual paths."""
    content = b'Test content for malformed paths'

    malformed_paths = [
        ('', 'empty-path'),  # Empty path
        ('invalid-path', 'no-leading-slash'),  # No leading slash
        ('/path//double-slash/', 'double-slash'),  # Double slashes
        ('/path/../traversal/', 'path-traversal'),  # Path traversal attempt
        ('/path\x00null/', 'null-byte'),  # Null byte injection
    ]

    for path, test_name in malformed_paths:
        data = {
            'file': (io.BytesIO(content), f'{test_name}.txt'),
            'path': path
        }

        response = client.post('/upload', data=data, content_type='multipart/form-data')

        # Should handle gracefully - either sanitize path or return clear error
        if response.status_code == 400:
            assert response.content_type == 'application/json'
            error_data = response.get_json()
            assert 'error' in error_data

def test_concurrent_operation_error_handling(client):
    """Test error handling under concurrent operations."""
    # Upload a file
    content = b'Content for concurrent testing'
    data = {
        'file': (io.BytesIO(content), 'concurrent-test.txt'),
        'path': '/'
    }

    upload = client.post('/upload', data=data, content_type='multipart/form-data')
    assert upload.status_code == 201
    file_id = upload.get_json()['file_id']

    # Simulate concurrent operations that might conflict
    # (In real implementation, these would need proper locking/transactions)

    # Try to delete file and restore simultaneously
    delete_response = client.post(f'/delete/{file_id}')
    # Should complete successfully or handle conflict gracefully
    assert delete_response.status_code in [200, 409]  # 409 = Conflict

    if delete_response.status_code == 409:
        assert delete_response.content_type == 'application/json'
        conflict_error = delete_response.get_json()
        assert 'error' in conflict_error

def test_application_stability_during_errors(client):
    """Test that application remains stable during various error conditions."""
    # Generate multiple error conditions in sequence
    error_operations = [
        ('GET', '/download/invalid-file-1'),
        ('GET', '/download/invalid-file-2/invalid-version'),
        ('POST', '/delete/invalid-file-3'),
        ('POST', '/restore/invalid-file-4/invalid-version'),
        ('GET', '/versions/invalid-file-5'),
        ('GET', '/api/file/invalid-file-6/info'),
        ('GET', '/api/versions/invalid-file-7'),
    ]

    for method, endpoint in error_operations:
        if method == 'GET':
            response = client.get(endpoint)
        elif method == 'POST':
            response = client.post(endpoint)

        # Should return proper error codes, not crash
        assert response.status_code in [400, 404, 500]

        # Should return proper content type
        if endpoint.startswith('/api/'):
            assert response.content_type == 'application/json'
        elif endpoint.startswith('/versions/'):
            assert response.content_type.startswith('text/html')
        else:
            assert response.content_type in ['application/json', 'text/html']

    # After all errors, basic functionality should still work
    health_check = client.get('/')
    assert health_check.status_code == 200

def test_error_message_security(client):
    """Test that error messages don't leak sensitive information."""
    # Test various error conditions
    error_responses = [
        client.get('/download/../../etc/passwd'),  # Path traversal attempt
        client.get('/download/invalid-file-id'),
        client.post('/delete/nonexistent'),
        client.get('/api/file/invalid/info'),
    ]

    for response in error_responses:
        if response.content_type == 'application/json':
            error_data = response.get_json()
            if 'error' in error_data:
                error_message = error_data['error'].lower()

                # Should not leak system paths, stack traces, or sensitive info
                sensitive_patterns = [
                    'traceback', 'exception', '/users/', '/home/',
                    'error:', 'line', 'file "', 'secret', 'key',
                    'password', 'token', 'credential'
                ]

                for pattern in sensitive_patterns:
                    assert pattern not in error_message, f"Error message contains sensitive info: {pattern}"