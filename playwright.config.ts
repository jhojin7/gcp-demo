import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // Test directory and patterns
  testDir: './tests',
  testMatch: /.*\.spec\.ts$/,

  // Global test configuration
  timeout: 30000,
  expect: {
    timeout: 5000
  },

  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // Retry configuration
  retries: process.env.CI ? 2 : 0,

  // Parallel execution
  workers: process.env.CI ? 1 : undefined,

  // Test result reporting
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    ['junit', { outputFile: 'test-results/junit.xml' }]
  ],

  // Shared settings for all projects
  use: {
    // Base URL for the application under test
    baseURL: 'http://localhost:5000',

    // Capture screenshot on failure
    screenshot: 'only-on-failure',

    // Record video on retry
    video: 'retain-on-failure',

    // Collect trace on failure
    trace: 'on-first-retry',

    // Browser context options
    acceptDownloads: true,

    // Ignore HTTPS errors for local development
    ignoreHTTPSErrors: true
  },

  // Browser and device projects
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    // Mobile viewport testing
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
  ],

  // Development server configuration
  webServer: {
    command: 'python run.py',
    port: 5000,
    reuseExistingServer: !process.env.CI,
    env: {
      FLASK_ENV: 'testing',
      GCP_MOCK_MODE: 'true'
    }
  },
});