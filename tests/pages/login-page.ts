import { Page, Locator, expect } from '@playwright/test';
import { BasePage } from './base-page';

export class LoginPage extends BasePage {
  // Form elements
  readonly usernameInput: Locator;
  readonly passwordInput: Locator;
  readonly loginButton: Locator;
  readonly rememberMeCheckbox: Locator;

  // Links
  readonly forgotPasswordLink: Locator;
  readonly signUpLink: Locator;

  // Error and success messages
  readonly loginErrorMessage: Locator;
  readonly loginSuccessMessage: Locator;

  // Form validation
  readonly usernameError: Locator;
  readonly passwordError: Locator;
  readonly formValidationError: Locator;

  // Loading states
  readonly loginSubmitSpinner: Locator;

  // Social login (if available)
  readonly googleLoginButton: Locator;
  readonly githubLoginButton: Locator;

  // Page elements
  readonly loginForm: Locator;
  readonly pageHeader: Locator;
  readonly pageDescription: Locator;

  // Session and logout
  readonly logoutButton: Locator;
  readonly userMenu: Locator;
  readonly userProfile: Locator;

  constructor(page: Page) {
    super(page, '/login');

    // Form elements
    this.usernameInput = page.locator('[data-testid="username"], #username, input[name="username"]');
    this.passwordInput = page.locator('[data-testid="password"], #password, input[name="password"]');
    this.loginButton = page.locator('[data-testid="login-button"], .login-button, button[type="submit"]');
    this.rememberMeCheckbox = page.locator('[data-testid="remember-me"], #remember-me');

    // Links
    this.forgotPasswordLink = page.locator('[data-testid="forgot-password"], .forgot-password');
    this.signUpLink = page.locator('[data-testid="sign-up"], .sign-up');

    // Error and success messages
    this.loginErrorMessage = page.locator('[data-testid="login-error"], .login-error');
    this.loginSuccessMessage = page.locator('[data-testid="login-success"], .login-success');

    // Form validation
    this.usernameError = page.locator('[data-testid="username-error"], .username-error');
    this.passwordError = page.locator('[data-testid="password-error"], .password-error');
    this.formValidationError = page.locator('[data-testid="form-error"], .form-error');

    // Loading states
    this.loginSubmitSpinner = page.locator('[data-testid="login-spinner"], .login-spinner');

    // Social login
    this.googleLoginButton = page.locator('[data-testid="google-login"], .google-login');
    this.githubLoginButton = page.locator('[data-testid="github-login"], .github-login');

    // Page elements
    this.loginForm = page.locator('[data-testid="login-form"], .login-form, form');
    this.pageHeader = page.locator('[data-testid="login-header"], .login-header, h1');
    this.pageDescription = page.locator('[data-testid="login-description"], .login-description');

    // Session and logout
    this.logoutButton = page.locator('[data-testid="logout"], .logout');
    this.userMenu = page.locator('[data-testid="user-menu"], .user-menu');
    this.userProfile = page.locator('[data-testid="user-profile"], .user-profile');
  }

  /**
   * Login with username and password
   */
  async login(username: string, password: string): Promise<void> {
    await this.enterUsername(username);
    await this.enterPassword(password);
    await this.clickLoginButton();
  }

  /**
   * Login with remember me option
   */
  async loginWithRememberMe(username: string, password: string): Promise<void> {
    await this.enterUsername(username);
    await this.enterPassword(password);
    await this.rememberMeCheckbox.check();
    await this.clickLoginButton();
  }

  /**
   * Logout from the application
   */
  async logout(): Promise<void> {
    // Try user menu first
    if (await this.isElementVisible(this.userMenu)) {
      await this.userMenu.click();
      await this.waitForElement(this.logoutButton);
    }

    if (await this.isElementVisible(this.logoutButton)) {
      await this.clickAndWaitForNavigation(this.logoutButton);
    }
  }

  /**
   * Check if user is logged in
   */
  async isLoggedIn(): Promise<boolean> {
    // Check if we're redirected away from login page or if user elements are visible
    const currentUrl = this.getCurrentUrl();
    const isOnLoginPage = currentUrl.includes('/login');
    const hasUserMenu = await this.isElementVisible(this.userMenu);
    const hasUserProfile = await this.isElementVisible(this.userProfile);

    return !isOnLoginPage || hasUserMenu || hasUserProfile;
  }

  /**
   * Enter username
   */
  async enterUsername(username: string): Promise<void> {
    await this.waitForElement(this.usernameInput);
    await this.fillInput(this.usernameInput, username);
  }

  /**
   * Enter password
   */
  async enterPassword(password: string): Promise<void> {
    await this.waitForElement(this.passwordInput);
    await this.fillInput(this.passwordInput, password);
  }

  /**
   * Click login button
   */
  async clickLoginButton(): Promise<void> {
    await this.waitForElement(this.loginButton);
    await this.loginButton.click();

    // Wait for either success (navigation) or error message
    try {
      await Promise.race([
        this.page.waitForURL(/^(?!.*\/login).*$/, { timeout: 10000 }), // Wait for navigation away from login
        this.waitForElement(this.loginErrorMessage)
      ]);
    } catch {
      // Neither happened within timeout, continue
    }

    await this.waitForLoadingToComplete();
  }

  /**
   * Check if login error is visible
   */
  async isLoginErrorVisible(): Promise<boolean> {
    return await this.isElementVisible(this.loginErrorMessage);
  }

  /**
   * Get login error message
   */
  async getLoginErrorMessage(): Promise<string> {
    if (await this.isLoginErrorVisible()) {
      return await this.getElementText(this.loginErrorMessage);
    }
    return '';
  }

  /**
   * Check if login success message is visible
   */
  async isLoginSuccessVisible(): Promise<boolean> {
    return await this.isElementVisible(this.loginSuccessMessage);
  }

  /**
   * Get login success message
   */
  async getLoginSuccessMessage(): Promise<string> {
    if (await this.isLoginSuccessVisible()) {
      return await this.getElementText(this.loginSuccessMessage);
    }
    return '';
  }

  /**
   * Check for form validation errors
   */
  async hasFormValidationErrors(): Promise<boolean> {
    const usernameError = await this.isElementVisible(this.usernameError);
    const passwordError = await this.isElementVisible(this.passwordError);
    const formError = await this.isElementVisible(this.formValidationError);

    return usernameError || passwordError || formError;
  }

  /**
   * Get all validation errors
   */
  async getValidationErrors(): Promise<string[]> {
    const errors: string[] = [];

    if (await this.isElementVisible(this.usernameError)) {
      errors.push(await this.getElementText(this.usernameError));
    }

    if (await this.isElementVisible(this.passwordError)) {
      errors.push(await this.getElementText(this.passwordError));
    }

    if (await this.isElementVisible(this.formValidationError)) {
      errors.push(await this.getElementText(this.formValidationError));
    }

    return errors;
  }

  /**
   * Check if login form is loading
   */
  async isLoginLoading(): Promise<boolean> {
    return await this.isElementVisible(this.loginSubmitSpinner);
  }

  /**
   * Click forgot password link
   */
  async clickForgotPassword(): Promise<void> {
    await this.forgotPasswordLink.click();
    await this.waitForLoad();
  }

  /**
   * Click sign up link
   */
  async clickSignUp(): Promise<void> {
    await this.signUpLink.click();
    await this.waitForLoad();
  }

  /**
   * Login with Google (if available)
   */
  async loginWithGoogle(): Promise<void> {
    if (await this.isElementVisible(this.googleLoginButton)) {
      await this.googleLoginButton.click();
      await this.waitForLoad();
    }
  }

  /**
   * Login with GitHub (if available)
   */
  async loginWithGithub(): Promise<void> {
    if (await this.isElementVisible(this.githubLoginButton)) {
      await this.githubLoginButton.click();
      await this.waitForLoad();
    }
  }

  /**
   * Check if social login options are available
   */
  async hasSocialLoginOptions(): Promise<boolean> {
    const hasGoogle = await this.isElementVisible(this.googleLoginButton);
    const hasGithub = await this.isElementVisible(this.githubLoginButton);
    return hasGoogle || hasGithub;
  }

  /**
   * Check if login form is visible
   */
  async isLoginFormVisible(): Promise<boolean> {
    return await this.isElementVisible(this.loginForm);
  }

  /**
   * Get page header text
   */
  async getPageHeader(): Promise<string> {
    return await this.getElementText(this.pageHeader);
  }

  /**
   * Get page description text
   */
  async getPageDescription(): Promise<string> {
    return await this.getElementText(this.pageDescription);
  }

  /**
   * Wait for login page to load
   */
  async waitForLoginPageToLoad(): Promise<void> {
    await this.waitForElement(this.loginForm);
    await this.waitForElement(this.usernameInput);
    await this.waitForElement(this.passwordInput);
    await this.waitForElement(this.loginButton);
  }

  /**
   * Clear login form
   */
  async clearLoginForm(): Promise<void> {
    await this.usernameInput.clear();
    await this.passwordInput.clear();
    if (await this.rememberMeCheckbox.isChecked()) {
      await this.rememberMeCheckbox.uncheck();
    }
  }

  /**
   * Check if remember me is checked
   */
  async isRememberMeChecked(): Promise<boolean> {
    return await this.rememberMeCheckbox.isChecked();
  }

  /**
   * Get current user information (if logged in)
   */
  async getCurrentUser(): Promise<string> {
    if (await this.isElementVisible(this.userProfile)) {
      return await this.getElementText(this.userProfile);
    }
    return '';
  }

  /**
   * Wait for logout to complete
   */
  async waitForLogout(): Promise<void> {
    await this.waitForUrl(/.*\/login.*/, 10000);
    await this.waitForLoginPageToLoad();
  }

  /**
   * Check if login button is enabled
   */
  async isLoginButtonEnabled(): Promise<boolean> {
    return await this.loginButton.isEnabled();
  }

  /**
   * Submit login form with Enter key
   */
  async submitWithEnter(): Promise<void> {
    await this.passwordInput.press('Enter');
    await this.waitForLoadingToComplete();
  }
}