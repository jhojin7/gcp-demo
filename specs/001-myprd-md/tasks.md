# Tasks: GCP Cloud Storage Versioned File Manager

**Input**: Design documents from `/Users/hojinjang/dev/gcp-demo/specs/001-myprd-md/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: Flask app structure with `app.py`, `gcp_storage.py`, `config.py`, `templates/`, `static/`
- **Tests**: `tests/contract/`, `tests/integration/`, `tests/unit/`
- Based on PRD structure decision: Flask single-project layout

## Phase 3.1: Setup
- [x] T001 Create Flask project structure with templates/, static/, and service modules
- [x] T002 Initialize Python project with Flask, google-cloud-storage, python-dateutil dependencies in requirements.txt
- [x] T003 [P] Configure pytest setup in tests/ directory with conftest.py

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

### Contract Tests
- [x] T004 [P] Contract test GET / (file browser) in tests/contract/test_file_browser.py
- [x] T005 [P] Contract test POST /upload in tests/contract/test_upload.py
- [x] T006 [P] Contract test GET /download/{file_id} in tests/contract/test_download.py
- [x] T007 [P] Contract test GET /download/{file_id}/{version_id} in tests/contract/test_download_version.py
- [x] T008 [P] Contract test POST /delete/{file_id} in tests/contract/test_delete.py
- [x] T009 [P] Contract test GET /versions/{file_id} in tests/contract/test_versions.py
- [x] T010 [P] Contract test POST /restore/{file_id}/{version_id} in tests/contract/test_restore.py
- [x] T011 [P] Contract test GET /api/files in tests/contract/test_api_files.py
- [x] T012 [P] Contract test GET /api/versions/{file_id} in tests/contract/test_api_versions.py
- [x] T013 [P] Contract test GET /api/file/{file_id}/info in tests/contract/test_api_file_info.py

### Integration Tests (Test Scenarios from Quickstart)
- [x] T014 [P] Integration test file upload and versioning in tests/integration/test_upload_versioning.py
- [x] T015 [P] Integration test version history and restoration in tests/integration/test_version_history.py
- [x] T016 [P] Integration test file download operations in tests/integration/test_download_operations.py
- [x] T017 [P] Integration test file deletion and recovery in tests/integration/test_deletion_recovery.py
- [x] T018 [P] Integration test folder navigation in tests/integration/test_folder_navigation.py
- [x] T019 [P] Integration test error handling in tests/integration/test_error_handling.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)

### Data Models and GCP Service Layer
- [x] T020 [P] File model class in models/file.py with validation and state transitions
- [x] T021 [P] FileVersion model class in models/file_version.py with metadata handling
- [x] T022 [P] User model class in models/user.py with ownership context
- [x] T023 [P] Folder model class in models/folder.py with virtual path logic
- [x] T024 [P] Operation model class in models/operation.py with audit tracking
- [x] T025 GCP Storage service class in gcp_storage.py with authentication and versioning
- [x] T026 File service layer in services/file_service.py for file operations
- [x] T027 Version service layer in services/version_service.py for version management

### Flask Application and Configuration
- [x] T028 Main Flask application in app.py with blueprints and routing
- [x] T029 Configuration management in config.py for GCP credentials and settings
- [x] T030 Error handling middleware and custom error pages

### Web Endpoints Implementation
- [x] T031 File browser endpoint GET / in app.py with folder navigation
- [x] T032 File upload endpoint POST /upload in app.py with versioning
- [x] T033 Current file download GET /download/{file_id} in app.py
- [x] T034 Version-specific download GET /download/{file_id}/{version_id} in app.py
- [x] T035 File deletion endpoint POST /delete/{file_id} in app.py
- [x] T036 Version history page GET /versions/{file_id} in app.py
- [x] T037 Version restore endpoint POST /restore/{file_id}/{version_id} in app.py

### API Endpoints Implementation
- [x] T038 Files list API GET /api/files in app.py
- [x] T039 Version history API GET /api/versions/{file_id} in app.py
- [x] T040 File info API GET /api/file/{file_id}/info in app.py

## Phase 3.4: Integration

### Frontend Templates and Static Files
- [x] T041 [P] Base template in templates/base.html with navigation and layout
- [x] T042 [P] File browser template in templates/index.html with upload form
- [x] T043 [P] Version history template in templates/versions.html with restore buttons
- [x] T044 [P] Basic CSS styling in static/style.css for file browser and version views
- [x] T045 [P] JavaScript interactions in static/script.js for AJAX operations

### Security and Validation
- [ ] T046 Input validation and file type restrictions
- [ ] T047 File size limits and quota enforcement
- [ ] T048 Metadata sanitization and security headers
- [ ] T049 User context and ownership enforcement

### Logging and Monitoring
- [ ] T050 Request/response logging setup
- [ ] T051 GCP operation audit logging
- [ ] T052 Error tracking and debugging tools

## Phase 3.5: Polish

### Unit Tests
- [ ] T053 [P] Unit tests for File model in tests/unit/test_file_model.py
- [ ] T054 [P] Unit tests for FileVersion model in tests/unit/test_file_version_model.py
- [ ] T055 [P] Unit tests for GCP service layer in tests/unit/test_gcp_storage.py
- [ ] T056 [P] Unit tests for file service layer in tests/unit/test_file_service.py
- [ ] T057 [P] Unit tests for validation logic in tests/unit/test_validation.py

### Performance and Documentation
- [ ] T058 Performance optimization for file listing and metadata queries
- [ ] T059 [P] Update README.md with setup and usage instructions
- [ ] T060 [P] Add configuration examples and environment setup guide
- [ ] T061 Execute complete quickstart validation scenarios
- [ ] T062 Code cleanup and remove duplication

## Dependencies
- Setup (T001-T003) before all other tasks
- Contract tests (T004-T013) before any implementation
- Integration tests (T014-T019) before core implementation
- Models (T020-T024) before services (T025-T027)
- Services before Flask app (T028) and endpoints (T031-T040)
- Core implementation (T020-T040) before frontend (T041-T045)
- Integration features (T046-T052) before polish (T053-T062)

## Parallel Example
```
# Setup Phase - Run in sequence
T001 → T002 → T003

# Contract Tests Phase - Run all in parallel
Task: "Contract test GET / (file browser) in tests/contract/test_file_browser.py"
Task: "Contract test POST /upload in tests/contract/test_upload.py"
Task: "Contract test GET /download/{file_id} in tests/contract/test_download.py"
Task: "Contract test GET /download/{file_id}/{version_id} in tests/contract/test_download_version.py"
Task: "Contract test POST /delete/{file_id} in tests/contract/test_delete.py"
Task: "Contract test GET /versions/{file_id} in tests/contract/test_versions.py"
Task: "Contract test POST /restore/{file_id}/{version_id} in tests/contract/test_restore.py"
Task: "Contract test GET /api/files in tests/contract/test_api_files.py"
Task: "Contract test GET /api/versions/{file_id} in tests/contract/test_api_versions.py"
Task: "Contract test GET /api/file/{file_id}/info in tests/contract/test_api_file_info.py"

# Integration Tests Phase - Run all in parallel
Task: "Integration test file upload and versioning in tests/integration/test_upload_versioning.py"
Task: "Integration test version history and restoration in tests/integration/test_version_history.py"
Task: "Integration test file download operations in tests/integration/test_download_operations.py"
Task: "Integration test file deletion and recovery in tests/integration/test_deletion_recovery.py"
Task: "Integration test folder navigation in tests/integration/test_folder_navigation.py"
Task: "Integration test error handling in tests/integration/test_error_handling.py"

# Models Phase - Run all in parallel
Task: "File model class in models/file.py with validation and state transitions"
Task: "FileVersion model class in models/file_version.py with metadata handling"
Task: "User model class in models/user.py with ownership context"
Task: "Folder model class in models/folder.py with virtual path logic"
Task: "Operation model class in models/operation.py with audit tracking"
```

## Notes
- [P] tasks = different files, no dependencies between tasks
- Verify all tests fail before implementing features
- Follow TDD strictly: Red → Green → Refactor
- Commit after each completed task
- GCP service account must be configured before testing
- All file operations must preserve version history
- Ensure constitutional compliance throughout implementation

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - file-management-api.yaml: 7 endpoints → 7 contract tests [P]
   - data-api.yaml: 3 endpoints → 3 contract tests [P]

2. **From Data Model**:
   - 5 entities (File, FileVersion, User, Folder, Operation) → 5 model tasks [P]
   - Service layer tasks for GCP interactions and business logic

3. **From Quickstart Scenarios**:
   - 6 test scenarios → 6 integration tests [P]
   - Performance and security validation tasks

4. **Ordering**:
   - Setup → Contract Tests → Integration Tests → Models → Services → Endpoints → Frontend → Integration → Polish
   - Constitutional requirements enforced throughout

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (10 contract tests for 10 endpoints)
- [x] All entities have model tasks (5 model tasks for 5 entities)
- [x] All tests come before implementation (TDD enforced)
- [x] Parallel tasks truly independent (different files, no shared state)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] All quickstart scenarios covered in integration tests
- [x] Constitutional requirements addressed in implementation tasks