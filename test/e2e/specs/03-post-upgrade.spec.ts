import { test, expect } from '../fixtures'
import { shoot } from '../helpers/screenshot'
import { signInSso } from '../helpers/auth'
import { openFilesSource, upgradeFolderPrefix } from '../helpers/files'

test('data created before the upgrade is still there', async ({ page }) => {
  await signInSso(page)
  await expect(page).toHaveURL(/\/files\/device/)
  await openFilesSource(page)
  const folder = page.locator(`a[aria-label^="${upgradeFolderPrefix}"]`).first()
  await expect(folder).toBeVisible()
  const name = await folder.getAttribute('aria-label')
  await folder.dblclick()
  await expect(page.locator(`a[aria-label="breadcrumb-link-${name}"]`)).toBeVisible()
  await shoot(page, 'files-after-upgrade')
})
