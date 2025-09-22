import { Page, Locator, expect } from '@playwright/test';

export abstract class BasePage {
  readonly page: Page;
  readonly url: string;

  // Common page elements
  readonly header: Locator;
  readonly navigation: Locator;
  readonly content: Locator;
  readonly footer: Locator;
  readonly loadingSpinner: Locator;
  readonly errorMessage: Locator;
  readonly successMessage: Locator;

  constructor(page: Page, url: string) {
    this.page = page;
    this.url = url;

    // Common selectors that should exist on all pages
    this.header = page.locator('header, .header, [data-testid="header"]');
    this.navigation = page.locator('nav, .navigation, [data-testid="navigation"]');
    this.content = page.locator('main, .content, [data-testid="content"]');
    this.footer = page.locator('footer, .footer, [data-testid="footer"]');
    this.loadingSpinner = page.locator('.loading, .spinner, [data-testid="loading"]');
    this.errorMessage = page.locator('.error, .error-message, [data-testid="error"]');
    this.successMessage = page.locator('.success, .success-message, [data-testid="success"]');
  }

  /**
   * Navigate to this page
   */
  async goto(): Promise<void> {
    await this.page.goto(this.url);
    await this.waitForLoad();
  }

  /**
   * Check if the page is loaded by waiting for key elements
   */
  async isLoaded(): Promise<boolean> {
    try {
      await this.waitForLoad();
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get the page title
   */
  async getTitle(): Promise<string> {
    return await this.page.title();
  }

  /**
   * Wait for the page to load completely
   */
  async waitForLoad(): Promise<void> {
    // Wait for network to be idle
    await this.page.waitForLoadState('networkidle');

    // Wait for loading spinner to disappear if it exists
    await this.waitForLoadingToComplete();
  }

  /**
   * Wait for any loading indicators to disappear
   */
  async waitForLoadingToComplete(): Promise<void> {
    try {
      // Wait for loading spinner to be hidden (if it exists)
      await this.loadingSpinner.waitFor({ state: 'hidden', timeout: 10000 });
    } catch {
      // Loading spinner might not exist, which is fine
    }
  }

  /**
   * Check if an error message is visible
   */
  async isErrorVisible(): Promise<boolean> {
    try {
      await this.errorMessage.waitFor({ state: 'visible', timeout: 1000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get the error message text
   */
  async getErrorMessage(): Promise<string> {
    if (await this.isErrorVisible()) {
      return await this.errorMessage.textContent() || '';
    }
    return '';
  }

  /**
   * Check if a success message is visible
   */
  async isSuccessVisible(): Promise<boolean> {
    try {
      await this.successMessage.waitFor({ state: 'visible', timeout: 1000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get the success message text
   */
  async getSuccessMessage(): Promise<string> {
    if (await this.isSuccessVisible()) {
      return await this.successMessage.textContent() || '';
    }
    return '';
  }

  /**
   * Wait for an element to be visible
   */
  async waitForElement(locator: Locator, timeout = 30000): Promise<void> {
    await locator.waitFor({ state: 'visible', timeout });
  }

  /**
   * Wait for an element to be hidden
   */
  async waitForElementToHide(locator: Locator, timeout = 30000): Promise<void> {
    await locator.waitFor({ state: 'hidden', timeout });
  }

  /**
   * Click an element and wait for navigation if expected
   */
  async clickAndWaitForNavigation(locator: Locator): Promise<void> {
    await Promise.all([
      this.page.waitForLoadState('networkidle'),
      locator.click()
    ]);
  }

  /**
   * Fill a form input field
   */
  async fillInput(locator: Locator, value: string): Promise<void> {
    await locator.clear();
    await locator.fill(value);
  }

  /**
   * Upload a file using input element
   */
  async uploadFile(inputLocator: Locator, filePath: string): Promise<void> {
    await inputLocator.setInputFiles(filePath);
  }

  /**
   * Take a screenshot for debugging
   */
  async takeScreenshot(name: string): Promise<void> {
    await this.page.screenshot({
      path: `test-results/screenshots/${name}-${Date.now()}.png`,
      fullPage: true
    });
  }

  /**
   * Scroll to an element
   */
  async scrollToElement(locator: Locator): Promise<void> {
    await locator.scrollIntoViewIfNeeded();
  }

  /**
   * Get current URL
   */
  getCurrentUrl(): string {
    return this.page.url();
  }

  /**
   * Wait for URL to match pattern
   */
  async waitForUrl(urlPattern: string | RegExp, timeout = 30000): Promise<void> {
    await this.page.waitForURL(urlPattern, { timeout });
  }

  /**
   * Refresh the page
   */
  async refresh(): Promise<void> {
    await this.page.reload();
    await this.waitForLoad();
  }

  /**
   * Go back in browser history
   */
  async goBack(): Promise<void> {
    await this.page.goBack();
    await this.waitForLoad();
  }

  /**
   * Check if element is visible
   */
  async isElementVisible(locator: Locator): Promise<boolean> {
    try {
      await locator.waitFor({ state: 'visible', timeout: 1000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get element text content
   */
  async getElementText(locator: Locator): Promise<string> {
    return await locator.textContent() || '';
  }

  /**
   * Wait for element to contain specific text
   */
  async waitForText(locator: Locator, text: string, timeout = 30000): Promise<void> {
    await expect(locator).toContainText(text, { timeout });
  }

  /**
   * Close any open modals or dialogs
   */
  async closeModal(): Promise<void> {
    const modalCloseButton = this.page.locator('.modal-close, .close, [data-testid="close-modal"]');
    if (await this.isElementVisible(modalCloseButton)) {
      await modalCloseButton.click();
    }
  }
}