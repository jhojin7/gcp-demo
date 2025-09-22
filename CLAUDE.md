# gcp-demo Development Guidelines

Auto-generated from all feature plans. Last updated: 2025-09-22

## Active Technologies
- Python 3.11+ + Flask, Google Cloud Storage Python client, datetime utilities (001-myprd-md)

## Project Structure
```
backend/
frontend/
tests/
```

## Commands
cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style
Python 3.11+: Follow standard conventions

## Recent Changes
- 001-myprd-md: Completed core implementation of GCP Cloud Storage Versioned File Manager
  - ✅ All data models (File, FileVersion, User, Folder, Operation)
  - ✅ GCP Storage service layer with authentication and versioning
  - ✅ File and version service layers
  - ✅ Complete Flask web application with all endpoints
  - ✅ Frontend templates with drag-drop upload, version history UI
  - ✅ CSS styling and JavaScript interactions
  - ✅ Error handling and configuration management
  - ✅ All contract and integration tests written (ready for testing with GCP setup)

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->