import { Page, expect } from '@playwright/test'

export const upgradeFolderPrefix = 'upgrade-survivor-'

export function item(page: Page, name: string) {
  return page.locator(`a[aria-label="${name}"]`)
}

export async function openFilesSource(page: Page) {
  await page.locator('a.source-button[aria-label="files"]').click()
  await expect(page.locator('[data-testid="file-actions-button"]')).toBeVisible()
}

export async function createFolder(page: Page, name: string) {
  await page.locator('[data-testid="file-actions-button"]').click()
  await page.locator('button[aria-label="New folder"]').click()
  await page.locator('input[aria-label="New Folder Name"]').fill(name)
  await page.locator('button[aria-label="Create"]').click()
  await expect(item(page, name)).toBeVisible()
}

export async function createFile(page: Page, name: string) {
  await page.locator('[data-testid="file-actions-button"]').click()
  await page.locator('button[aria-label="New file"]').click()
  await page.locator('button[aria-label="Empty file"]').click()
  await page.locator('input[aria-label="FileName Field"]').fill(name)
  await page.locator('button[aria-label="Create"]').click()
  await expect(item(page, name)).toBeVisible()
}
