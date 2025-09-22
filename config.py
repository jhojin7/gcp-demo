import os
import logging
from typing import Optional


class Config:
    """
    Configuration management for GCP Cloud Storage File Manager.
    Loads settings from environment variables with sensible defaults.
    """

    # Flask Configuration
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
    PORT = int(os.environ.get('FLASK_PORT', '5000'))

    # GCP Configuration
    GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID')
    GCP_BUCKET_NAME = os.environ.get('GCP_BUCKET_NAME')
    GCP_SERVICE_ACCOUNT_KEY_PATH = os.environ.get('GCP_SERVICE_ACCOUNT_KEY_PATH')

    # File Upload Configuration
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_FILE_SIZE_MB', '100')) * 1024 * 1024  # Default 100MB
    UPLOAD_ALLOWED_EXTENSIONS = os.environ.get(
        'UPLOAD_ALLOWED_EXTENSIONS',
        'txt,pdf,png,jpg,jpeg,gif,doc,docx,xls,xlsx,ppt,pptx,zip,tar,gz'
    ).split(',')

    # Security Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', '/tmp/uploads')
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',') if os.environ.get('ALLOWED_HOSTS') else []

    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
    LOG_FORMAT = os.environ.get(
        'LOG_FORMAT',
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # User Context Configuration (for future authentication)
    DEFAULT_USER_ID = os.environ.get('DEFAULT_USER_ID', 'default-user')
    DEFAULT_USER_NAME = os.environ.get('DEFAULT_USER_NAME', 'Default User')

    # Feature Flags
    ENABLE_VERSION_CLEANUP = os.environ.get('ENABLE_VERSION_CLEANUP', 'False').lower() in ('true', '1', 'yes')
    ENABLE_AUDIT_LOGGING = os.environ.get('ENABLE_AUDIT_LOGGING', 'True').lower() in ('true', '1', 'yes')
    ENABLE_PERFORMANCE_METRICS = os.environ.get('ENABLE_PERFORMANCE_METRICS', 'False').lower() in ('true', '1', 'yes')

    @classmethod
    def validate_required_settings(cls) -> list:
        """
        Validate that all required configuration is present.

        Returns:
            List of missing configuration keys
        """
        missing = []

        required_settings = [
            'GCP_PROJECT_ID',
            'GCP_BUCKET_NAME'
        ]

        for setting in required_settings:
            if not getattr(cls, setting):
                missing.append(setting)

        return missing

    @classmethod
    def setup_logging(cls):
        """Configure application logging."""
        logging.basicConfig(
            level=getattr(logging, cls.LOG_LEVEL),
            format=cls.LOG_FORMAT
        )

        # Set specific logger levels
        if cls.DEBUG:
            logging.getLogger('werkzeug').setLevel(logging.INFO)
            logging.getLogger('google.cloud').setLevel(logging.INFO)
        else:
            logging.getLogger('werkzeug').setLevel(logging.WARNING)
            logging.getLogger('google.cloud').setLevel(logging.WARNING)

    @classmethod
    def get_gcp_config(cls) -> dict:
        """Get GCP-specific configuration as dictionary."""
        return {
            'project_id': cls.GCP_PROJECT_ID,
            'bucket_name': cls.GCP_BUCKET_NAME,
            'service_account_key_path': cls.GCP_SERVICE_ACCOUNT_KEY_PATH
        }

    @classmethod
    def get_flask_config(cls) -> dict:
        """Get Flask-specific configuration as dictionary."""
        return {
            'SECRET_KEY': cls.SECRET_KEY,
            'DEBUG': cls.DEBUG,
            'MAX_CONTENT_LENGTH': cls.MAX_CONTENT_LENGTH
        }

    @classmethod
    def is_file_allowed(cls, filename: str) -> bool:
        """
        Check if file extension is allowed for upload.

        Args:
            filename: Name of file to check

        Returns:
            True if file extension is allowed
        """
        if not filename or '.' not in filename:
            return False

        extension = filename.rsplit('.', 1)[1].lower()
        return extension in [ext.strip().lower() for ext in cls.UPLOAD_ALLOWED_EXTENSIONS]

    @classmethod
    def get_upload_config(cls) -> dict:
        """Get upload-specific configuration as dictionary."""
        return {
            'max_size_mb': cls.MAX_CONTENT_LENGTH // (1024 * 1024),
            'allowed_extensions': cls.UPLOAD_ALLOWED_EXTENSIONS,
            'upload_folder': cls.UPLOAD_FOLDER
        }

    @classmethod
    def create_upload_directory(cls):
        """Create upload directory if it doesn't exist."""
        if not os.path.exists(cls.UPLOAD_FOLDER):
            os.makedirs(cls.UPLOAD_FOLDER, exist_ok=True)

    @classmethod
    def print_configuration_summary(cls):
        """Print configuration summary for debugging."""
        print("=== GCP File Manager Configuration ===")
        print(f"Flask Debug: {cls.DEBUG}")
        print(f"Flask Host: {cls.HOST}")
        print(f"Flask Port: {cls.PORT}")
        print(f"GCP Project: {cls.GCP_PROJECT_ID}")
        print(f"GCP Bucket: {cls.GCP_BUCKET_NAME}")
        print(f"Service Account Key: {'Set' if cls.GCP_SERVICE_ACCOUNT_KEY_PATH else 'Not Set'}")
        print(f"Max File Size: {cls.MAX_CONTENT_LENGTH // (1024 * 1024)}MB")
        print(f"Allowed Extensions: {', '.join(cls.UPLOAD_ALLOWED_EXTENSIONS)}")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print(f"Audit Logging: {cls.ENABLE_AUDIT_LOGGING}")
        print("=" * 40)


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG = False
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """Testing-specific configuration."""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    # Use in-memory or test-specific settings
    GCP_PROJECT_ID = 'test-project'
    GCP_BUCKET_NAME = 'test-bucket'


# Configuration factory
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': Config
}


def get_config(config_name: Optional[str] = None) -> Config:
    """
    Get configuration class based on environment.

    Args:
        config_name: Configuration name ('development', 'production', 'testing')
                    If None, uses FLASK_ENV environment variable

    Returns:
        Configuration class instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    return config_map.get(config_name, Config)