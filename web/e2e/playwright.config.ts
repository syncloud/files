import { defineConfig, devices } from '@playwright/test'

const domain = process.env.PLAYWRIGHT_DOMAIN || 'bookworm.com'
const baseURL = `https://files.${domain}`

export default defineConfig({
  testDir: './specs',
  timeout: 120_000,
  expect: { timeout: 20_000 },
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: [['list']],
  globalTeardown: './global-teardown.ts',
  use: {
    baseURL,
    ignoreHTTPSErrors: true,
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'on'
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'], baseURL, ignoreHTTPSErrors: true } }
  ]
})
