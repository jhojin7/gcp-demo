# Data Model: Playwright End-to-End Testing Suite

## Core Test Entities

### TestSuite
Represents a collection of related test scenarios for a specific application area.

**Attributes**:
- `name`: string - Descriptive name (e.g., "File Upload Tests", "Version Management Tests")
- `description`: string - Purpose and scope of the test suite
- `browser`: BrowserType - Target browser for execution
- `baseUrl`: string - Application base URL for testing
- `timeout`: number - Default timeout for suite operations
- `retries`: number - Number of retry attempts for flaky tests

**Relationships**:
- Contains multiple TestScenario entities
- Belongs to TestConfiguration

### TestScenario
Individual test case validating specific user workflow or functionality.

**Attributes**:
- `id`: string - Unique identifier for the test scenario
- `title`: string - Human-readable test description
- `category`: TestCategory - Classification (upload, download, version, auth, error)
- `priority`: Priority - High, Medium, Low based on user workflow criticality
- `browser`: BrowserType[] - List of browsers to test against
- `preconditions`: string[] - Required application state before test
- `steps`: TestStep[] - Ordered list of test actions
- `expectedResult`: string - Expected outcome description
- `tags`: string[] - Labels for test organization and filtering

**Relationships**:
- Belongs to TestSuite
- Contains multiple TestStep entities
- Produces TestResult when executed

### TestStep
Individual action within a test scenario.

**Attributes**:
- `stepNumber`: number - Order of execution within scenario
- `action`: ActionType - Type of action (click, type, upload, verify, navigate)
- `selector`: string - CSS/XPath selector for target element
- `input`: string - Data to input (text, file path, etc.)
- `expected`: string - Expected outcome of the step
- `screenshot`: boolean - Whether to capture screenshot after step
- `waitCondition`: WaitCondition - What to wait for before next step

**State Transitions**:
- Pending → Executing → Completed/Failed
- Failed steps can trigger retries or test termination

### TestConfiguration
Environment and browser configuration for test execution.

**Attributes**:
- `environment`: Environment - Local, staging, production
- `browsers`: BrowserConfig[] - Browser-specific settings
- `viewport`: Viewport - Screen dimensions for testing
- `baseUrl`: string - Application URL for testing
- `timeout`: TimeoutConfig - Various timeout settings
- `parallelism`: number - Number of parallel test workers
- `retries`: number - Global retry configuration

### TestResult
Outcome and metrics from test scenario execution.

**Attributes**:
- `scenarioId`: string - Reference to executed TestScenario
- `browser`: BrowserType - Browser used for execution
- `status`: TestStatus - Passed, Failed, Skipped, Timeout
- `startTime`: timestamp - Test execution start
- `endTime`: timestamp - Test execution completion
- `duration`: number - Execution time in milliseconds
- `error`: ErrorInfo - Failure details if status is Failed
- `screenshots`: string[] - Captured screenshot file paths
- `video`: string - Recorded video file path
- `logs`: LogEntry[] - Browser console and network logs

**Relationships**:
- References TestScenario that was executed
- Contains ErrorInfo for failures
- Contains multiple LogEntry records

### PageObject
Encapsulation of page interactions and element selectors for maintainability.

**Attributes**:
- `pageName`: string - Logical page name (e.g., "FileBrowser", "VersionHistory")
- `url`: string - Page URL pattern
- `selectors`: ElementSelector[] - Named element selectors
- `methods`: PageMethod[] - Available page interaction methods

**Relationships**:
- Used by TestStep entities for page interactions
- Contains ElementSelector and PageMethod collections

## Supporting Types

### BrowserType
Enumeration: Chrome, Firefox, Safari, Edge

### TestCategory
Enumeration: Upload, Download, Version, Navigation, Authentication, Error, Performance

### Priority
Enumeration: High, Medium, Low

### ActionType
Enumeration: Click, Type, Upload, Download, Navigate, Verify, Wait, Screenshot

### TestStatus
Enumeration: Pending, Running, Passed, Failed, Skipped, Timeout

### Environment
Enumeration: Local, Staging, Production

### WaitCondition
Object with properties:
- `type`: WaitType (element, network, timeout)
- `selector`: string (for element waits)
- `timeout`: number (maximum wait time)

## Validation Rules

### TestSuite Validation
- Name must be unique within project
- Must contain at least one TestScenario
- Timeout values must be positive integers
- Browser list cannot be empty

### TestScenario Validation
- ID must be unique across all suites
- Must have at least one TestStep
- Priority must be specified
- Tags cannot contain spaces or special characters

### TestStep Validation
- Step numbers must be sequential starting from 1
- Selector must be valid CSS/XPath expression
- Action type must match input requirements
- Screenshot boolean defaults to false

### TestConfiguration Validation
- BaseUrl must be valid HTTP/HTTPS URL
- Viewport dimensions must be positive
- Parallelism must be between 1 and CPU core count
- Timeout values must be positive

## Test Data Management

### TestFixture
Represents reusable test data and application state.

**Attributes**:
- `name`: string - Fixture identifier
- `data`: object - Test data payload
- `setup`: string[] - Setup commands to prepare fixture
- `cleanup`: string[] - Cleanup commands after test completion
- `dependencies`: string[] - Other fixtures this depends on

### MockData
Mock responses for GCP service interactions during testing.

**Attributes**:
- `service`: string - GCP service name (storage, auth)
- `operation`: string - API operation being mocked
- `request`: object - Expected request parameters
- `response`: object - Mock response payload
- `httpStatus`: number - HTTP status code to return
- `delay`: number - Simulated network delay in milliseconds

This data model supports comprehensive test organization, execution tracking, and maintenance while ensuring tests remain isolated and reliable.