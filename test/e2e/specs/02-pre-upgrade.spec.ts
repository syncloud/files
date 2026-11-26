import { test, expect } from '../fixtures'
import { shoot } from '../helpers/screenshot'
import { signInSso } from '../helpers/auth'
import { item, openFilesSource, createFolder, upgradeFolderPrefix } from '../helpers/files'

test('create data that must survive the upgrade', async ({ page }) => {
  const folder = `${upgradeFolderPrefix}${Date.now()}`
  await signInSso(page)
  await openFilesSource(page)
  await createFolder(page, folder)
  await expect(item(page, folder)).toBeVisible()
  await shoot(page, 'files-before-upgrade')
})
