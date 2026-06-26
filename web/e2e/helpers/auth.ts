import { Page, TestInfo } from '@playwright/test'

const onAuthHost = (page: Page) => {
  try { return new URL(page.url()).host.startsWith('auth.') } catch { return false }
}

async function shootStep (page: Page, info: TestInfo | undefined, name: string) {
  if (!info) return
  try { await page.screenshot({ path: info.outputPath(name), fullPage: false }) } catch {}
}

export async function loginViaAuthelia (
  page: Page,
  baseURL: string,
  username: string,
  password: string,
  info?: TestInfo
) {
  await page.goto(baseURL)
  await page.waitForLoadState('networkidle').catch(() => {})
  await shootStep(page, info, 'login-00-landing.png')

  if (!onAuthHost(page)) {
    const oidcButton = page
      .getByRole('button', { name: /openid|sign in|login|continue/i })
      .or(page.getByRole('link', { name: /openid|sign in|login|continue/i }))
      .first()
    await Promise.race([
      page.waitForURL((url) => new URL(url.toString()).host.startsWith('auth.'), { timeout: 30_000 }).catch(() => {}),
      oidcButton.waitFor({ state: 'visible', timeout: 30_000 }).catch(() => {})
    ])
    if (!onAuthHost(page) && await oidcButton.isVisible().catch(() => false)) {
      await Promise.all([
        page.waitForURL((url) => new URL(url.toString()).host.startsWith('auth.'), { timeout: 30_000 }).catch(() => {}),
        oidcButton.click()
      ])
    }
    await page.waitForLoadState('networkidle').catch(() => {})
    await shootStep(page, info, 'login-01-after-signin.png')
  }

  if (onAuthHost(page)) {
    const userSel = 'input[name="username"], input#username-textfield, input[autocomplete="username"], input[type="text"]'
    const passSel = 'input[name="password"], input#password-textfield, input[autocomplete="current-password"], input[type="password"]'
    const submitSel = 'button#sign-in-button, button[type="submit"], button:has-text("Sign in"), button:has-text("Login")'

    await page.locator(userSel).first().waitFor({ state: 'visible', timeout: 20_000 })
    await page.locator(userSel).first().fill(username)
    await page.locator(passSel).first().fill(password)
    await Promise.all([
      page.waitForURL((url) => !new URL(url.toString()).host.startsWith('auth.'), { timeout: 30_000 }).catch(() => {}),
      page.locator(submitSel).first().click()
    ])
    await page.waitForLoadState('networkidle').catch(() => {})
    await shootStep(page, info, 'login-02-after-auth.png')
  }

  try {
    await page.locator('#app').first().waitFor({ state: 'attached', timeout: 30_000 })
  } catch (e) {
    const title = await page.title().catch(() => '?')
    throw new Error(`login did not land on the app: url=${page.url()} title="${title}"`)
  }
  await page.waitForLoadState('networkidle').catch(() => {})
}
