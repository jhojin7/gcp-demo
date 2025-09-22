# Quickstart: Playwright End-to-End Testing Suite

This guide provides the essential steps to set up, run, and validate the Playwright testing suite for the GCP Cloud Storage File Manager.

## Prerequisites

- Node.js 18+ installed
- Flask application running locally on port 5000
- Test fixtures and mock data available
- GCP service mocked for testing environment

## Quick Setup

### 1. Install Dependencies
```bash
# Navigate to project root
cd /path/to/gcp-demo

# Install Playwright and dependencies
npm install @playwright/test
npx playwright install

# Install TypeScript for contract validation
npm install -D typescript @types/node
```

### 2. Configuration Verification
```bash
# Verify Playwright configuration exists
ls tests/playwright.config.ts

# Validate test environment
npm run test:setup
```

### 3. Environment Setup
```bash
# Set testing environment variables
export FLASK_ENV=testing
export GCP_MOCK_MODE=true
export BASE_URL=http://localhost:5000

# Start Flask application in testing mode
python run.py &
```

## Essential Test Execution

### Run Core Test Suite (5 minutes)
```bash
# Execute critical path tests
npx playwright test --grep "@critical"

# Verify core functionality works
npx playwright test tests/core-functionality.spec.ts
```

### Cross-Browser Validation (10 minutes)
```bash
# Run tests across all configured browsers
npx playwright test --project=chromium --project=firefox --project=webkit

# Generate test report
npx playwright show-report
```

### Mobile Responsiveness Check (3 minutes)
```bash
# Test mobile viewport compatibility
npx playwright test --project="Mobile Chrome"
```

## Validation Steps

### 1. File Upload Workflow
**Expected Duration**: 2 minutes
```bash
# Test file upload functionality
npx playwright test tests/file-upload.spec.ts

# Verify upload success criteria:
# ✓ File appears in browser list
# ✓ File metadata is correct
# ✓ Version count is 1
```

### 2. Version Management Workflow
**Expected Duration**: 3 minutes
```bash
# Test version creation and management
npx playwright test tests/version-management.spec.ts

# Verify version functionality:
# ✓ Multiple versions can be created
# ✓ Version history is displayed correctly
# ✓ Rollback creates new current version
```

### 3. Error Handling Validation
**Expected Duration**: 2 minutes
```bash
# Test error scenarios
npx playwright test tests/error-handling.spec.ts

# Verify error handling:
# ✓ Invalid file uploads are rejected
# ✓ Network failures are handled gracefully
# ✓ User-friendly error messages are shown
```

## Quick Debugging

### View Test Results
```bash
# Open HTML test report
npx playwright show-report

# View failed test screenshots
ls test-results/*/test-failed-*.png

# Check browser console logs
cat test-results/*/browser-logs.txt
```

### Re-run Failed Tests
```bash
# Run only failed tests from last execution
npx playwright test --last-failed

# Run specific test with debug mode
npx playwright test tests/specific-test.spec.ts --debug
```

## Success Criteria Validation

After completing the quickstart, verify these outcomes:

### ✅ Test Infrastructure
- [ ] All dependencies installed successfully
- [ ] Playwright configuration loads without errors
- [ ] Test environment variables are set correctly
- [ ] Flask application starts in testing mode

### ✅ Core Test Coverage
- [ ] File upload tests pass on all browsers
- [ ] File download tests complete successfully
- [ ] Version management tests validate correctly
- [ ] Authentication flow tests work as expected

### ✅ Error Handling
- [ ] Invalid upload scenarios are caught
- [ ] Network failure simulation works
- [ ] GCP service mocking functions correctly
- [ ] Error messages are user-friendly

### ✅ Cross-Browser Support
- [ ] Chrome/Chromium tests pass
- [ ] Firefox tests complete without issues
- [ ] Safari/WebKit tests run successfully (if available)
- [ ] Mobile viewport tests validate correctly

### ✅ Performance Metrics
- [ ] Full test suite completes within 10 minutes
- [ ] Individual test scenarios run under 30 seconds
- [ ] Parallel execution works correctly
- [ ] Test reports generate successfully

## Troubleshooting Common Issues

### Flask Application Not Starting
```bash
# Check if port 5000 is available
lsof -i :5000

# Verify environment configuration
python -c "import os; print(os.environ.get('FLASK_ENV'))"
```

### Browser Installation Issues
```bash
# Reinstall browsers
npx playwright install --force

# Check browser installation
npx playwright --version
```

### Test Failures Due to Timing
```bash
# Increase timeout in playwright.config.ts
# timeout: 60000  // 60 seconds

# Add explicit waits in tests
await page.waitForSelector('.file-upload-complete')
```

### GCP Mock Not Working
```bash
# Verify mock service is running
curl http://localhost:5000/api/health

# Check mock configuration
cat config/testing.env
```

## Next Steps

After successful quickstart validation:

1. **Customize Tests**: Modify test scenarios for specific use cases
2. **CI/CD Integration**: Set up automated test execution in GitHub Actions
3. **Extended Coverage**: Add performance and accessibility tests
4. **Monitoring**: Configure test result reporting and alerting

**Estimated Total Setup Time**: 15-20 minutes
**Estimated Test Execution Time**: 8-12 minutes for full suite