# GCP Cloud Storage Versioned File Manager

This project is a web application for managing versioned files in Google Cloud Storage. It provides a "Time Machine"-like interface for your files, allowing you to upload, download, restore, and manage different versions of your files with a complete and immutable audit trail.

## Features

- **File Versioning**: Automatically creates a new version of a file on every upload.
- **Version History**: View the complete history of a file, including who made changes and when.
- **Restore**: Restore any previous version of a file.
- **Download**: Download the current or any historical version of a file.
- **Soft Delete**: Files are soft-deleted, preserving their history for future recovery.
- **Folder Organization**: Organize files in a hierarchical folder structure.

## Prerequisites

- Python 3.11+
- Google Cloud Platform project with the Cloud Storage API enabled.
- A GCP service account with a JSON key file.
- A GCP bucket with versioning enabled.

## Setup

1.  **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

2.  **Install libmagic**:

    On macOS with Homebrew:
    ```bash
    brew install libmagic
    ```

    On Debian/Ubuntu:
    ```bash
    sudo apt-get install libmagic1
    ```

3.  **Install python-dotenv**:

    ```bash
    pip install python-dotenv
    ```

4.  **Configure Environment Variables**:

    Create a `.env` file in the root of the project by copying the `.env.example` file:

    ```bash
    cp .env.example .env
    ```

    Then, edit the `.env` file with your GCP project details:

    ```
    FLASK_ENV=development
    GCP_PROJECT_ID="your-gcp-project-id"
    GCP_BUCKET_NAME="your-gcs-bucket-name"
    GCP_SERVICE_ACCOUNT_KEY_PATH="/path/to/your/service-account-key.json"
    FLASK_SECRET_KEY="a-strong-and-secret-key"
    ```

## Running the Application

Once the setup is complete, you can run the application with:

```bash
python app.py
```

The application will be available at `http://localhost:5000`.
