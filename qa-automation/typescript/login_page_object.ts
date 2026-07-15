// LoginPage.ts
// Page Object Model for the application's login flow.
// Encapsulates locators and actions for the login form using
// Playwright's recommended locator strategies and explicit waits.

import { expect, Locator, Page } from '@playwright/test';

export class LoginPage {
  private readonly page: Page;
  private readonly usernameInput: Locator;
  private readonly passwordInput: Locator;
  private readonly submitButton: Locator;
  private readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    // Prefer accessible, role-based locators over CSS/XPath for resilience.
    this.usernameInput = page.getByLabel('Username');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Log in' });
    this.errorMessage = page.getByRole('alert');
  }

  async goto(): Promise<void> {
    await this.page.goto('/login');
    // Ensure the form is interactive before proceeding.
    await this.usernameInput.waitFor({ state: 'visible' });
  }

  async login(username: string, password: string): Promise<void> {
    await this.usernameInput.fill(username);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectLoginSuccess(expectedUrlPart: string): Promise<void> {
    // Explicit wait for navigation rather than relying on implicit timing.
    await this.page.waitForURL(new RegExp(expectedUrlPart));
  }

  async expectLoginError(message: string): Promise<void> {
    await expect(this.errorMessage).toBeVisible();
    await expect(this.errorMessage).toHaveText(message);
  }

  async isSubmitButtonEnabled(): Promise<boolean> {
    return this.submitButton.isEnabled();
  }
}
