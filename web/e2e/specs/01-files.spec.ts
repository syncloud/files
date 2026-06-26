import { test, expect } from '@playwright/test'
import { shoot } from '../helpers/screenshot'
import { loginViaAuthelia } from '../helpers/auth'
import { ssh } from '../helpers/ssh'

const baseURL = `https://files.${process.env.PLAYWRIGHT_DOMAIN || 'bookworm.com'}`
const username = process.env.PLAYWRIGHT_USER || 'user'
const password = process.env.PLAYWRIGHT_PASSWORD || 'Password1'

test('login via OpenID and browse files', async ({ page }, info) => {
  const marker = `syncloud-e2e-${info.project.name}.txt`
  const sourcePath = ssh(
    `sed -n 's/.*path: *"\\(.*\\)"/\\1/p' /var/snap/files/current/config/config.yaml | head -1`
  ).trim()
  ssh(`echo hello > '${sourcePath}/${marker}' && chown files:files '${sourcePath}/${marker}'`, { throw: false })

  await loginViaAuthelia(page, baseURL, username, password, info)
  await shoot(page, info, 'index')

  await expect(page.locator('#app')).toBeVisible()
  expect(new URL(page.url()).host).toBe(new URL(baseURL).host)

  await expect(page.getByText(marker)).toBeVisible({ timeout: 30_000 })
  await shoot(page, info, 'listing')
})
