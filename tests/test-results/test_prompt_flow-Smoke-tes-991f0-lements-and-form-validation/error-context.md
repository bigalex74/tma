# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: test_prompt_flow.spec.js >> Smoke test: verify UI elements and form validation
- Location: test_prompt_flow.spec.js:3:1

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: page.goto: Test timeout of 30000ms exceeded.
Call log:
  - navigating to "http://127.0.0.1:8000/files", waiting until "load"

```

# Test source

```ts
  1  | const { test, expect } = require('@playwright/test');
  2  | 
  3  | test('Smoke test: verify UI elements and form validation', async ({ page }) => {
> 4  |   await page.goto('/files');
     |              ^ Error: page.goto: Test timeout of 30000ms exceeded.
  5  |   
  6  |   // Ждем, пока селекты заполнятся (init вызывается в конце скрипта)
  7  |   await page.waitForSelector('#sel-file option:nth-child(2)');
  8  |   
  9  |   // Проверка селектов
  10 |   const fileOptions = await page.locator('#sel-file option').count();
  11 |   expect(fileOptions).toBeGreaterThan(1);
  12 |   
  13 |   // Проверка кнопки
  14 |   const startBtn = page.locator('#btn-start');
  15 |   await expect(startBtn).toBeDisabled();
  16 | 
  17 |   // Выбор значений
  18 |   await page.selectOption('#sel-file', { index: 1 });
  19 |   await page.selectOption('#sel-bp', { index: 1 });
  20 |   await page.selectOption('#sel-pp', { index: 1 });
  21 |   
  22 |   // Проверка разблокировки
  23 |   await expect(startBtn).toBeEnabled();
  24 | });
  25 | 
```