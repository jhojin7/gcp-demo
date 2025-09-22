import { test, expect, chromium, firefox, webkit } from '@playwright/test';

test.describe('Browser Launch Configuration Contract', () => {
  test('should successfully launch Chromium browser', async () => {
    const browser = await chromium.launch();
    expect(browser).toBeTruthy();

    const context = await browser.newContext();
    expect(context).toBeTruthy();

    const page = await context.newPage();
    expect(page).toBeTruthy();

    await page.close();
    await context.close();
    await browser.close();
  });

  test('should successfully launch Firefox browser', async () => {
    const browser = await firefox.launch();
    expect(browser).toBeTruthy();

    const context = await browser.newContext();
    expect(context).toBeTruthy();

    const page = await context.newPage();
    expect(page).toBeTruthy();

    await page.close();
    await context.close();
    await browser.close();
  });

  test('should successfully launch WebKit browser', async () => {
    const browser = await webkit.launch();
    expect(browser).toBeTruthy();

    const context = await browser.newContext();
    expect(context).toBeTruthy();

    const page = await context.newPage();
    expect(page).toBeTruthy();

    await page.close();
    await context.close();
    await browser.close();
  });

  test('should create browser context with correct configuration', async () => {
    const browser = await chromium.launch();
    const context = await browser.newContext({
      acceptDownloads: true,
      ignoreHTTPSErrors: true,
      viewport: { width: 1280, height: 720 }
    });

    expect(context).toBeTruthy();

    const page = await context.newPage();
    const viewport = page.viewportSize();
    expect(viewport).toEqual({ width: 1280, height: 720 });

    await page.close();
    await context.close();
    await browser.close();
  });

  test('should support mobile device emulation', async () => {
    const browser = await chromium.launch();
    const context = await browser.newContext({
      userAgent: 'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Mobile Safari/537.36',
      viewport: { width: 393, height: 851 },
      isMobile: true,
      hasTouch: true
    });

    expect(context).toBeTruthy();

    const page = await context.newPage();
    const viewport = page.viewportSize();
    expect(viewport).toEqual({ width: 393, height: 851 });

    await page.close();
    await context.close();
    await browser.close();
  });

  test('should handle browser context isolation', async () => {
    const browser = await chromium.launch();

    // Create two separate contexts
    const context1 = await browser.newContext();
    const context2 = await browser.newContext();

    const page1 = await context1.newPage();
    const page2 = await context2.newPage();

    // Contexts should be isolated
    expect(context1).not.toBe(context2);
    expect(page1).not.toBe(page2);

    await page1.close();
    await page2.close();
    await context1.close();
    await context2.close();
    await browser.close();
  });
});