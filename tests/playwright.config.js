const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './',
  use: {
    baseURL: 'http://172.20.0.5:8000',
    headless: true,
  },
});
