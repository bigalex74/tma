const { test, expect } = require('@playwright/test');

test('should create a new prompt via UI', async ({ page }) => {
  await page.goto('/');
  
  // Добавляем промпт
  await page.click('#add-btn');
  await page.fill('#f-name', 'E2E Test Prompt');
  await page.fill('#f-prompt', 'This is a test prompt content');
  
  // Сохраняем
  await page.click('#save-btn');
  
  // Проверяем появление в списке (после перезагрузки или обновления)
  await page.goto('/');
  await expect(page.locator('text=E2E Test Prompt')).toBeVisible();
});
