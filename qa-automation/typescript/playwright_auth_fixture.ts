/**
 * Custom Playwright fixture that authenticates once (via UI login) and
 * caches the resulting storage state on disk. Subsequent tests / workers
 * reuse the cached session instead of repeating the login flow, which
 * significantly speeds up test suites that require authentication.
 */
import { test as base, expect, type Page, type BrowserContext } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const STORAGE_STATE_PATH = path.join(__dirname, '.auth', 'user.json');

type AuthFixtures = {
  authenticatedPage: Page;
};

export const test = base.extend<AuthFixtures>({
  // Override the default `context` fixture to inject a reusable storage state.
  context: async ({ browser }, use) => {
    if (!fs.existsSync(STORAGE_STATE_PATH)) {
      // No cached session yet: log in via the UI once and persist the state.
      const loginContext = await browser.newContext();
      const loginPage = await loginContext.newPage();

      await loginPage.goto('/login');
      await loginPage.fill('#username', process.env.TEST_USER ?? 'testuser');
      await loginPage.fill('#password', process.env.TEST_PASSWORD ?? 'testpass');
      await loginPage.click('button[type="submit"]');

      // Wait for a reliable post-login signal before saving state.
      await loginPage.waitForURL('**/dashboard');

      fs.mkdirSync(path.dirname(STORAGE_STATE_PATH), { recursive: true });
      await loginContext.storageState({ path: STORAGE_STATE_PATH });
      await loginContext.close();
    }

    // Every subsequent test/worker just loads the cached storage state.
    const context: BrowserContext = await browser.newContext({
      storageState: STORAGE_STATE_PATH,
    });

    await use(context);
    await context.close();
  },

  authenticatedPage: async ({ context }, use) => {
    const page = await context.newPage();
    await use(page);
    await page.close();
  },
});

export { expect };
