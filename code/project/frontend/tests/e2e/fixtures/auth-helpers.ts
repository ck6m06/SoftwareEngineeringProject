import { Page, expect } from '@playwright/test'
import { testRehomeData } from './rehome-test-data'

export async function loginAsValidMember(page: Page) {
  console.log('🔑 正在登入測試用戶:', testRehomeData.validMember.email)
  
  await page.goto('/login')
  await page.fill('#email', testRehomeData.validMember.email)
  await page.fill('#password', testRehomeData.validMember.password)
  await page.click('button[type="submit"]')
  
  // 檢查是否成功登入 (透過檢查是否離開登入頁面)
  try {
    await page.waitForURL(url => !url.pathname.includes('/login'), { timeout: 10000 })
    console.log('✅ 登入成功，已導航到:', page.url())
  } catch (error) {
    console.error('❌ 登入失敗 - 仍在登入頁面')
    
    // 檢查是否有錯誤訊息
    const errorMsg = await page.locator('.text-red-500, .error, .alert, [role="alert"]').textContent().catch(() => '無錯誤訊息')
    console.log('錯誤訊息:', errorMsg)
    
    throw new Error(`登入失敗: ${errorMsg}`)
  }
}

export async function loginAsAdmin(page: Page) {
  console.log('🔑 正在登入管理員帳號: admin@test.com')
  
  await page.goto('/login')
  await page.fill('#email', 'admin@test.com')
  await page.fill('#password', 'Admin123')
  await page.click('button[type="submit"]')
  
  // 檢查是否成功登入
  try {
    await page.waitForURL(url => !url.pathname.includes('/login'), { timeout: 10000 })
    console.log('✅ 管理員登入成功，已導航到:', page.url())
  } catch (error) {
    console.error('❌ 管理員登入失敗')
    throw error
  }
}

export async function logout(page: Page) {
  await page.click('[data-testid="user-menu"]')
  await page.click('[data-testid="logout-button"]')
  
  // 確認已登出
  await expect(page.getByTestId('login-button')).toBeVisible()
}

export async function registerNewUser(page: Page, userData = testRehomeData.validMember) {
  await page.goto('/register')
  
  await page.fill('[data-testid="email-input"]', userData.email)
  await page.fill('[data-testid="password-input"]', userData.password)
  await page.fill('[data-testid="password-confirm-input"]', userData.password)
  await page.fill('[data-testid="first-name-input"]', userData.firstName)
  await page.fill('[data-testid="last-name-input"]', userData.lastName)
  await page.fill('[data-testid="phone-input"]', userData.phone)
  
  await page.click('[data-testid="register-button"]')
  
  // 等待註冊成功訊息
  await expect(page.getByText('請檢查電子郵件進行驗證')).toBeVisible()
}

export async function verifyEmail(page: Page) {
  // 模擬電子郵件驗證流程
  // 在真實環境中，這裡會需要訪問驗證連結
  await page.goto('/auth/verify?token=mock-verification-token')
  await expect(page.getByText('電子郵件驗證成功')).toBeVisible()
}

export async function ensureLoggedOut(page: Page) {
  try {
    const userMenu = page.getByTestId('user-menu')
    if (await userMenu.isVisible({ timeout: 1000 })) {
      await logout(page)
    }
  } catch (error) {
    // 已經是登出狀態
  }
}