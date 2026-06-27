import { test, expect } from '@playwright/test'
import { shoot } from '../helpers/screenshot'
import { loginViaAuthelia } from '../helpers/auth'

const username = process.env.PLAYWRIGHT_USER!
const password = process.env.PLAYWRIGHT_PASSWORD!

test('browse read-only system source, create dir and file in writable source', async ({ page, baseURL }, info) => {
  const stamp = Date.now()
  const dir = `e2e-dir-${stamp}`
  const file = `note-${stamp}.txt`
  const content = `hello from syncloud e2e ${stamp}`

  await loginViaAuthelia(page, baseURL!, username, password)

  const acknowledge = page.locator('button[aria-label^="Acknowledge"]')
  await acknowledge.waitFor({ state: 'visible' })
  await shoot(page, info, '01-first-login-welcome')
  await acknowledge.click()
  await shoot(page, info, '02-logged-in')

  await page.locator('a.source-button[aria-label="device"]').click()
  await page.locator('a[aria-label="etc"]').waitFor({ state: 'visible' })
  await shoot(page, info, '03-device-root')

  await page.locator('a[aria-label="etc"]').dblclick()
  await page.locator('a[aria-label="breadcrumb-link-etc"]').waitFor({ state: 'visible' })
  await expect(page.locator('a[aria-label="passwd"]')).toBeVisible()
  await shoot(page, info, '04-etc-has-entries')

  await page.locator('a.source-button[aria-label="files"]').click()
  await page.locator('[data-testid="file-actions-button"]').waitFor({ state: 'visible' })
  await shoot(page, info, '05-files-source')

  await page.locator('[data-testid="file-actions-button"]').click()
  await page.locator('button[aria-label="New folder"]').click()
  await page.locator('input[aria-label="New Folder Name"]').fill(dir)
  await page.locator('button[aria-label="Create"]').click()
  await page.locator(`a[aria-label="${dir}"]`).waitFor({ state: 'visible' })
  await shoot(page, info, '06-dir-created')

  await page.locator(`a[aria-label="${dir}"]`).dblclick()
  await page.locator(`a[aria-label="breadcrumb-link-${dir}"]`).waitFor({ state: 'visible' })
  await shoot(page, info, '07-inside-dir')

  await page.locator('[data-testid="file-actions-button"]').click()
  await page.locator('button[aria-label="New file"]').click()
  await page.locator('input[aria-label="FileName Field"]').fill(file)
  await page.locator('button[aria-label="Create"]').click()
  await page.locator(`a[aria-label="${file}"]`).waitFor({ state: 'visible' })
  await shoot(page, info, '08-file-created')

  await page.locator(`a[aria-label="${file}"]`).dblclick()
  await page.locator('.ace_content').click()
  await page.keyboard.type(content)
  await shoot(page, info, '09-content-typed')

  await page.locator('.overflow-menu-button').click()
  await page.locator('button[aria-label="Save"]').click()
  await expect(page.locator('.notification-message, .toast-message').filter({ hasText: `${file} saved successfully` })).toBeVisible()
  await shoot(page, info, '10-saved')

  await page.locator('button[title="Close"]').click()
  await page.locator(`a[aria-label="${file}"]`).dblclick()
  await expect(page.locator('.ace_text-layer .ace_line').first()).toHaveText(content)
  await shoot(page, info, '11-reopened-content')
})
