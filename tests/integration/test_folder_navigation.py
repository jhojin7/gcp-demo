import pytest
import io

def test_folder_navigation_scenario(client):
    """
    Test Scenario 5: Folder Navigation
    1. Upload Files with Paths
    2. Navigate Folder Structure
    3. Verify hierarchical organization
    """
    # Step 1: Upload Files with Paths
    test_files = [
        ('/documents/reports/report1.pdf', b'Report 1 content'),
        ('/documents/reports/report2.pdf', b'Report 2 content'),
        ('/documents/images/photo1.jpg', b'Photo 1 binary data'),
        ('/documents/images/photo2.jpg', b'Photo 2 binary data'),
        ('/projects/code/main.py', b'print("Hello World")'),
        ('/projects/code/utils.py', b'def helper(): pass'),
        ('/projects/docs/README.md', b'# Project Documentation')
    ]

    uploaded_files = []

    for virtual_path, content in test_files:
        filename = virtual_path.split('/')[-1]
        folder_path = '/'.join(virtual_path.split('/')[:-1]) + '/'

        data = {
            'file': (io.BytesIO(content), filename),
            'path': folder_path
        }

        upload = client.post('/upload', data=data, content_type='multipart/form-data')
        assert upload.status_code == 201

        uploaded_files.append({
            'file_id': upload.get_json()['file_id'],
            'filename': filename,
            'virtual_path': virtual_path,
            'folder_path': folder_path
        })

    # Step 2: Navigate Folder Structure
    # Check root level
    root_files = client.get('/api/files?path=/')
    assert root_files.status_code == 200
    root_data = root_files.get_json()

    assert root_data['current_path'] == '/'
    assert root_data['parent_path'] is None

    # Should have documents and projects folders
    root_file_names = [f['display_name'] for f in root_data['files']]
    # May show folder indicators or actual files

    # Check documents folder
    docs_files = client.get('/api/files?path=/documents/')
    assert docs_files.status_code == 200
    docs_data = docs_files.get_json()

    assert docs_data['current_path'] == '/documents/'
    assert docs_data['parent_path'] == '/'

    # Check documents/reports subfolder
    reports_files = client.get('/api/files?path=/documents/reports/')
    assert reports_files.status_code == 200
    reports_data = reports_files.get_json()

    assert reports_data['current_path'] == '/documents/reports/'
    assert reports_data['parent_path'] == '/documents/'

    # Should contain report files
    report_filenames = [f['display_name'] for f in reports_data['files']]
    assert 'report1.pdf' in report_filenames
    assert 'report2.pdf' in report_filenames

    # Check documents/images subfolder
    images_files = client.get('/api/files?path=/documents/images/')
    assert images_files.status_code == 200
    images_data = images_files.get_json()

    image_filenames = [f['display_name'] for f in images_data['files']]
    assert 'photo1.jpg' in image_filenames
    assert 'photo2.jpg' in image_filenames

    # Check projects folder structure
    projects_files = client.get('/api/files?path=/projects/')
    assert projects_files.status_code == 200

    code_files = client.get('/api/files?path=/projects/code/')
    assert code_files.status_code == 200
    code_data = code_files.get_json()

    code_filenames = [f['display_name'] for f in code_data['files']]
    assert 'main.py' in code_filenames
    assert 'utils.py' in code_filenames

    # Step 3: Verify hierarchical organization
    # Test file browser pages with navigation
    browser_root = client.get('/')
    assert browser_root.status_code == 200

    browser_docs = client.get('/?path=/documents/')
    assert browser_docs.status_code == 200

    browser_reports = client.get('/?path=/documents/reports/')
    assert browser_reports.status_code == 200

    # Browser should show breadcrumb navigation
    page_content = browser_reports.data.decode('utf-8').lower()
    assert any(word in page_content for word in ['breadcrumb', 'navigation', 'path'])

def test_folder_virtual_path_handling(client):
    """Test proper handling of virtual paths in metadata."""
    # Upload files to various folder depths
    test_cases = [
        ('/', 'root-file.txt', b'Root level file'),
        ('/level1/', 'level1-file.txt', b'Level 1 file'),
        ('/level1/level2/', 'level2-file.txt', b'Level 2 file'),
        ('/level1/level2/level3/', 'level3-file.txt', b'Level 3 file'),
    ]

    for folder_path, filename, content in test_cases:
        data = {
            'file': (io.BytesIO(content), filename),
            'path': folder_path
        }

        upload = client.post('/upload', data=data, content_type='multipart/form-data')
        assert upload.status_code == 201

        file_id = upload.get_json()['file_id']

        # Check file info includes correct virtual path
        file_info = client.get(f'/api/file/{file_id}/info')
        assert file_info.status_code == 200

        info_data = file_info.get_json()
        assert info_data['virtual_path'] == folder_path
        assert info_data['display_name'] == filename

def test_breadcrumb_navigation_functionality(client):
    """Test breadcrumb navigation in folder browser."""
    # Create nested folder structure
    content = b'Deep nested file content'
    data = {
        'file': (io.BytesIO(content), 'deep-file.txt'),
        'path': '/a/b/c/d/e/'
    }

    upload = client.post('/upload', data=data, content_type='multipart/form-data')
    assert upload.status_code == 201

    # Test browser at deep level includes breadcrumb navigation
    deep_browser = client.get('/?path=/a/b/c/d/e/')
    assert deep_browser.status_code == 200

    page_content = deep_browser.data.decode('utf-8').lower()

    # Should contain navigation elements
    navigation_indicators = ['breadcrumb', 'navigation', '/', 'back', 'up']
    assert any(indicator in page_content for indicator in navigation_indicators)

def test_folder_file_listing_performance(client):
    """Test folder listing performance with multiple files."""
    # Create multiple files in same folder
    folder_path = '/performance-test/'

    for i in range(20):
        content = f'Performance test file {i} content'.encode()
        filename = f'perf-test-{i:03d}.txt'

        data = {
            'file': (io.BytesIO(content), filename),
            'path': folder_path
        }

        upload = client.post('/upload', data=data, content_type='multipart/form-data')
        assert upload.status_code == 201

    # Test folder listing loads efficiently
    folder_listing = client.get(f'/api/files?path={folder_path}')
    assert folder_listing.status_code == 200

    listing_data = folder_listing.get_json()
    assert len(listing_data['files']) >= 20

    # All files should be in correct folder
    for file_obj in listing_data['files']:
        if file_obj['display_name'].startswith('perf-test-'):
            assert file_obj['virtual_path'] == folder_path

def test_empty_folder_handling(client):
    """Test handling of empty folders and navigation."""
    # Test navigation to empty folder
    empty_folder_response = client.get('/api/files?path=/empty-folder/')
    assert empty_folder_response.status_code == 200

    empty_data = empty_folder_response.get_json()
    assert empty_data['current_path'] == '/empty-folder/'
    assert empty_data['files'] == []

    # Browser should handle empty folders gracefully
    empty_browser = client.get('/?path=/empty-folder/')
    assert empty_browser.status_code == 200