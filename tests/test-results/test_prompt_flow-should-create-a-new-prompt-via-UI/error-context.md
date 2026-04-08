# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test_prompt_flow.spec.js >> should create a new prompt via UI
- Location: test_prompt_flow.spec.js:3:1

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.goto: Test timeout of 30000ms exceeded.
Call log:
  - navigating to "http://172.20.0.5:8000/", waiting until "load"

```

# Test source

```ts
  1  | const { test, expect } = require('@playwright/test');
  2  | 
  3  | test('should create a new prompt via UI', async ({ page }) => {
> 4  |   await page.goto('/');
     |              ^ Error: page.goto: Test timeout of 30000ms exceeded.
  5  |   
  6  |   // Добавляем промпт
  7  |   await page.click('#add-btn');
  8  |   await page.fill('#f-name', 'E2E Test Prompt');
  9  |   await page.fill('#f-prompt', 'This is a test prompt content');
  10 |   
  11 |   // Сохраняем
  12 |   await page.click('#save-btn');
  13 |   
  14 |   // Проверяем появление в списке (после перезагрузки или обновления)
  15 |   await page.goto('/');
  16 |   await expect(page.locator('text=E2E Test Prompt')).toBeVisible();
  17 | });
  18 | 
```