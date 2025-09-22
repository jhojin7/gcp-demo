import pytest
import os
import tempfile
from unittest.mock import Mock, patch
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    from app import create_app

    # Create a temporary file to serve as test database
    db_fd, db_path = tempfile.mkstemp()

    app = create_app({
        'TESTING': True,
        'GCP_PROJECT_ID': 'test-project',
        'GCP_BUCKET_NAME': 'test-bucket',
        'GCP_SERVICE_ACCOUNT_KEY_PATH': 'test-key.json',
        'SECRET_KEY': 'test-secret'
    })

    with app.test_request_context():
        yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture
def mock_gcp_storage():
    """Mock GCP Storage client for testing."""
    with patch('google.cloud.storage.Client') as mock_client:
        mock_bucket = Mock()
        mock_client.return_value.bucket.return_value = mock_bucket
        yield mock_client, mock_bucket

@pytest.fixture
def sample_file_data():
    """Sample file data for testing."""
    return {
        'display_name': 'test_file.txt',
        'content': b'Test file content',
        'content_type': 'text/plain',
        'virtual_path': '/documents/',
        'owner_id': 'test_user'
    }