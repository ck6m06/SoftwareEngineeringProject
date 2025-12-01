import { Page, expect, Locator } from '@playwright/test'

export class NavigationPage {
  readonly page: Page
  readonly logo: Locator
  readonly mainMenu: Record<string, Locator>
  readonly userMenu: Locator
  readonly userMenuDropdown: Record<string, Locator>
  readonly mobileMenuToggle: Locator
  
  constructor(page: Page) {
    this.page = page
    this.logo = page.locator('a[href="/"]').first()
    this.mainMenu = {
      home: page.locator('a[href="/"]').nth(1), // 第二個首頁連結 (在導航中)
      animals: page.locator('a[href="/animals"]'),
      rehome: page.locator('a[href="/rehome-form"]'), // 實際的送養連結
      login: page.locator('a[href="/login"]'),
      register: page.locator('a[href="/register"]')
    }
    this.userMenu = page.locator('button').filter({ hasText: '👤' })
    this.userMenuDropdown = {
      profile: page.locator('a[href="/profile"]'),
      logout: page.locator('button').filter({ hasText: '登出' })
    }
    this.mobileMenuToggle = page.locator('button').filter({ has: page.locator('svg') }).last()
  }
  
  async goToHome() {
    await this.mainMenu.home.click()
    await expect(this.page).toHaveURL('/')
  }
  
  async goToAnimals() {
    await this.mainMenu.animals.click()
    await expect(this.page).toHaveURL('/animals')
  }
  
  async goToRehome() {
    console.log('🔗 正在點擊送養連結')
    await this.mainMenu.rehome.click()
    await expect(this.page).toHaveURL('/rehome-form')
  }
  
  async goToRehomeNew() {
    // 對於一般會員，直接導航到送養表單
    console.log('🔗 正在導航到送養表單頁面')
    await this.mainMenu.rehome.click()
    await expect(this.page).toHaveURL('/rehome-form')
  }
  
  async openUserMenu() {
    await this.userMenu.click()
    await expect(this.page.getByTestId('user-menu-dropdown')).toBeVisible()
  }
  
  async goToProfile() {
    await this.openUserMenu()
    await this.userMenuDropdown.profile.click()
    await expect(this.page).toHaveURL('/profile')
  }
  
  async goToMyPosts() {
    await this.openUserMenu()
    await this.userMenuDropdown.myPosts.click()
    await expect(this.page).toHaveURL('/my-posts')
  }
  
  async logout() {
    await this.openUserMenu()
    await this.userMenuDropdown.logout.click()
    
    // 確認登出成功
    await expect(this.page.getByTestId('login-button')).toBeVisible()
  }
  
  async expectUserLoggedIn(userName?: string) {
    await expect(this.userMenu).toBeVisible()
    if (userName) {
      await expect(this.page.getByText(`歡迎，${userName}`)).toBeVisible()
    }
  }
  
  async expectUserLoggedOut() {
    await expect(this.page.getByTestId('login-button')).toBeVisible()
    await expect(this.userMenu).not.toBeVisible()
  }
}