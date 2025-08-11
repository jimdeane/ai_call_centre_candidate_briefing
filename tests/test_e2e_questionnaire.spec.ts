import { test, expect } from '@playwright/test';

test('Submit correct answers to questionnaire', async ({ page }) => {
  await page.goto('http://localhost:5020/');
  await page.fill('input[name="qid"]', '1');
  await page.fill('input[name="session"]', 'session1');
  await page.fill('input[name="code"]', 'supersecretadmincode');
  await page.click('button[type="submit"]');
  await expect(page.locator('form')).toBeVisible();
  await page.fill('input[name="name"]', 'Test User');
  await page.check('input[name="q1"][value="Option A"]');
  await page.check('input[name="q2"][value="Option B"]');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL(/.*instructions.*/);
  await expect(page.locator('#instructions-md')).toBeVisible();
});

test('Submit incorrect answers to questionnaire', async ({ page }) => {
  await page.goto('http://localhost:5020/');
  await page.fill('input[name="qid"]', '1');
  await page.fill('input[name="session"]', 'session2');
  await page.fill('input[name="code"]', 'supersecretadmincode');
  await page.click('button[type="submit"]');
  await expect(page.locator('form')).toBeVisible();
  await page.fill('input[name="name"]', 'Test User');
  await page.check('input[name="q1"][value="Option B"]'); // incorrect
  await page.check('input[name="q2"][value="Option A"]'); // incorrect
  await page.click('button[type="submit"]');
  await expect(page.locator('form')).toContainText('Resubmit Incorrect Answers');
});
