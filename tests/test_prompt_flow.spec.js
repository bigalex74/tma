const { test, expect } = require('@playwright/test');

test('Smoke test: verify UI elements and form validation', async ({ page }) => {
  await page.goto('/files');
  
  // Ждем, пока селекты заполнятся (init вызывается в конце скрипта)
  await page.waitForSelector('#sel-file option:nth-child(2)');
  
  // Проверка селектов
  const fileOptions = await page.locator('#sel-file option').count();
  expect(fileOptions).toBeGreaterThan(1);
  
  // Проверка кнопки
  const startBtn = page.locator('#btn-start');
  await expect(startBtn).toBeDisabled();

  // Выбор значений
  await page.selectOption('#sel-file', { index: 1 });
  await page.selectOption('#sel-bp', { index: 1 });
  await page.selectOption('#sel-pp', { index: 1 });
  
  // Проверка разблокировки
  await expect(startBtn).toBeEnabled();
});
