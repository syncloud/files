import { Page, expect } from '@playwright/test'
import { env } from './env'

export const deviceUser = env('PLAYWRIGHT_DEVICE_USER')
export const devicePassword = env('PLAYWRIGHT_DEVICE_PASSWORD')

export async function signInSso(page: Page, onAuthelia: () => Promise<void> = async () => {}) {
  await page.addLocatorHandler(page.locator('button[aria-label^="Acknowledge"]'), async (button) => {
    await button.click()
  }, { times: 1 })

  await page.goto('/')
  await page.waitForURL((url) => url.host.startsWith('auth.'))
  await expect(page.locator('#username-textfield')).toBeVisible()
  await onAuthelia()

  await page.locator('#username-textfield').fill(deviceUser)
  await page.locator('#password-textfield').fill(devicePassword)
  await page.locator('#sign-in-button').click()

  const skipPasskey = page.getByRole('button', { name: 'Not now' })
  const sources = page.locator('a.source-button[aria-label="files"]')
  await expect(skipPasskey.or(sources)).toBeVisible({ timeout: 60_000 })
  if (await skipPasskey.isVisible()) {
    await skipPasskey.click()
  }
  await expect(sources).toBeVisible({ timeout: 60_000 })
}
