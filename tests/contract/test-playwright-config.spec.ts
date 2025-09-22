import { test, expect } from '@playwright/test';
import playwrightConfig from '../../playwright.config';

test.describe('Playwright Configuration Contract', () => {
  test('should have correct test directory', () => {
    expect(playwrightConfig.testDir).toBe('./tests');
  });

  test('should support all required browsers', () => {
    const projectNames = playwrightConfig.projects?.map(p => p.name);
    expect(projectNames).toContain('chromium');
    expect(projectNames).toContain('firefox');
    expect(projectNames).toContain('webkit');
    expect(projectNames).toContain('Mobile Chrome');
  });

  test('should have proper timeout configuration', () => {
    expect(playwrightConfig.timeout).toBe(30000);
    expect(playwrightConfig.expect?.timeout).toBe(5000);
  });

  test('should have correct base URL', () => {
    expect(playwrightConfig.use?.baseURL).toBe('http://localhost:5000');
  });

  test('should have reporter configuration', () => {
    expect(playwrightConfig.reporter).toEqual([
      ['html'],
      ['json', { outputFile: 'test-results/results.json' }],
      ['junit', { outputFile: 'test-results/junit.xml' }]
    ]);
  });

  test('should have web server configuration for Flask app', () => {
    expect(playwrightConfig.webServer).toEqual({
      command: 'python run.py',
      port: 5000,
      reuseExistingServer: !process.env.CI,
      env: {
        FLASK_ENV: 'testing',
        GCP_MOCK_MODE: 'true'
      }
    });
  });

  test('should have proper retry configuration', () => {
    // Should retry on CI, not retry locally
    if (process.env.CI) {
      expect(playwrightConfig.retries).toBe(2);
    } else {
      expect(playwrightConfig.retries).toBe(0);
    }
  });

  test('should have screenshot and video capture on failure', () => {
    expect(playwrightConfig.use?.screenshot).toBe('only-on-failure');
    expect(playwrightConfig.use?.video).toBe('retain-on-failure');
    expect(playwrightConfig.use?.trace).toBe('on-first-retry');
  });

  test('should allow downloads and ignore HTTPS errors', () => {
    expect(playwrightConfig.use?.acceptDownloads).toBe(true);
    expect(playwrightConfig.use?.ignoreHTTPSErrors).toBe(true);
  });
});