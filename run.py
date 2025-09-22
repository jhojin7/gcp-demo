#!/usr/bin/env python3
"""
Development runner for GCP File Manager
Loads environment variables and starts the Flask application
"""

import os
import sys
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    if env_file.exists():
        print("Loading environment variables from .env file...")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    print(f"  ✓ {key}")
    else:
        print("No .env file found. Make sure to set environment variables manually.")

def check_required_config():
    """Check if required configuration is present"""
    required_vars = [
        'GCP_PROJECT_ID',
        'GCP_BUCKET_NAME'
    ]

    missing = []
    for var in required_vars:
        if not os.environ.get(var) or os.environ.get(var) == f'your-{var.lower().replace("_", "-")}':
            missing.append(var)

    if missing:
        print("\n❌ Missing required configuration:")
        for var in missing:
            print(f"  - {var}")
        print("\nPlease update your .env file with actual GCP project details.")
        print("You can run the application anyway to see the interface, but GCP operations will fail.")
        return False

    print("\n✅ All required configuration present!")
    return True

def main():
    """Main entry point"""
    print("🚀 Starting GCP File Manager...")

    # Load environment variables
    load_env_file()

    # Check configuration
    config_ok = check_required_config()

    # Import and run the app
    try:
        from app import create_app

        app = create_app()

        print(f"\n🌐 Application will be available at:")
        print(f"   http://{app.config.get('HOST', 'localhost')}:{app.config.get('PORT', 5000)}")
        print("\n📋 Features available:")
        print("   - File browser with drag-drop upload")
        print("   - Version history and restore")
        print("   - Folder navigation")
        print("   - REST API endpoints")

        if not config_ok:
            print("\n⚠️  Note: GCP operations will fail until you configure:")
            print("   - GCP_PROJECT_ID: Your Google Cloud project ID")
            print("   - GCP_BUCKET_NAME: Your Cloud Storage bucket name")
            print("   - GCP_SERVICE_ACCOUNT_KEY_PATH: Path to service account JSON file")

        print("\n🎯 Press Ctrl+C to stop the server")
        print("=" * 50)

        # Run the app
        app.run(
            host=os.environ.get('FLASK_HOST', '127.0.0.1'),
            port=int(os.environ.get('FLASK_PORT', 5000)),
            debug=os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
        )

    except ImportError as e:
        print(f"\n❌ Failed to import application: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Failed to start application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()