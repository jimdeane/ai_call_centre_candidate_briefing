import { test, expect } from '@playwright/test';

test('Admin panel loads and shows codes and submissions', async ({ page }) => {
  await page.goto('http://localhost:5020/admin?code=supersecretadmincode');
  await expect(page.locator('.codes-pane')).toBeVisible();
  await expect(page.locator('.submissions-list')).toBeVisible();
  await expect(page.locator('.details-pane')).toBeVisible();
});

test('Manage questionnaires page loads', async ({ page }) => {
  await page.goto('http://localhost:5020/manage_questionnaires');
  await expect(page.locator('h1')).toContainText('Manage Questionnaires');
  await expect(page.locator('ul')).toBeVisible();
});
