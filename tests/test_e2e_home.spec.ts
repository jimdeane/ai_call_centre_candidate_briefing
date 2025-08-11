import { test, expect } from '@playwright/test';

test('Home page loads and form is present', async ({ page }) => {
  await page.goto('http://localhost:5020/');
  await expect(page.locator('form')).toBeVisible();
  await expect(page.locator('input[name="qid"]')).toBeVisible();
  await expect(page.locator('input[name="session"]')).toBeVisible();
  await expect(page.locator('input[name="code"]')).toBeVisible();
});
