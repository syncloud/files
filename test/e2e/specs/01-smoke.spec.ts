import { test, expect } from '../fixtures'
import { shoot } from '../helpers/screenshot'
import { signInSso } from '../helpers/auth'
import { item, openFilesSource, createFolder, createFile } from '../helpers/files'

test('sign in, browse the device source, create a folder, then edit and reopen a file', async ({ page }) => {
  const stamp = Date.now()
  const dir = `e2e-dir-${stamp}`
  const file = `note-${stamp}.txt`
  const content = `hello from syncloud e2e ${stamp}`

  await test.step('sign in', async () => {
    await signInSso(page, async () => {
      await shoot(page, 'authelia-login')
    })
    await expect(page).toHaveURL(/\/files\/device/)
    await shoot(page, 'logged-in')
  })

  await test.step('browse the device source', async () => {
    await expect(item(page, 'etc')).toBeVisible()
    await shoot(page, 'device-root')
    await item(page, 'etc').dblclick()
    await expect(page.locator('a[aria-label="breadcrumb-link-etc"]')).toBeVisible()
    await expect(item(page, 'passwd')).toBeVisible()
    await shoot(page, 'device-etc')
  })

  await test.step('create a folder in the files source', async () => {
    await openFilesSource(page)
    await shoot(page, 'files-source')
    await createFolder(page, dir)
    await shoot(page, 'folder-created')
  })

  await test.step('create, edit and reopen a file', async () => {
    await createFile(page, file)
    await shoot(page, 'file-created')

    await item(page, file).dblclick()
    await page.locator('.ace_content').click()
    await page.keyboard.type(content)
    await shoot(page, 'file-edited')
    await page.keyboard.press('Control+s')
    await expect(page.getByText(`${file} saved successfully.`)).toBeVisible()
    await shoot(page, 'file-saved')

    await page.locator('#button-toggle-navbar').click()
    await item(page, file).dblclick()
    await expect(page.locator('.ace_text-layer')).toContainText(content)
    await shoot(page, 'file-reopened')
  })
})
