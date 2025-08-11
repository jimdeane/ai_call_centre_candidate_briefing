import { test, expect } from '@playwright/test';

test('Invalid access code or session shows error', async ({ page }) => {
  await page.goto('http://localhost:5020/');
  await page.fill('input[name="qid"]', '1');
  await page.fill('input[name="session"]', 'bad_session');
  await page.fill('input[name="code"]', 'bad_code');
  await page.click('button[type="submit"]');
  await expect(page.locator('body')).toContainText('Invalid or missing session or code');
});
