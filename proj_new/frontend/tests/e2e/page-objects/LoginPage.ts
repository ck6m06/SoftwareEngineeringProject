import { Page, expect, Locator } from '@playwright/test'

export class LoginPage {
  readonly page: Page
  readonly emailInput: Locator
  readonly passwordInput: Locator
  readonly loginButton: Locator
  readonly registerLink: Locator
  readonly forgotPasswordLink: Locator
  readonly errorMessage: Locator
  readonly successMessage: Locator
  readonly socialLoginButtons: Record<string, Locator>
  
  constructor(page: Page) {
    this.page = page
    this.emailInput = page.getByTestId('email-input')
    this.passwordInput = page.getByTestId('password-input')
    this.loginButton = page.getByTestId('login-button')
    this.registerLink = page.getByTestId('register-link')
    this.forgotPasswordLink = page.getByTestId('forgot-password-link')
    this.errorMessage = page.getByTestId('error-message')
    this.successMessage = page.getByTestId('success-message')
    this.socialLoginButtons = {
      google: page.getByTestId('google-login'),
      facebook: page.getByTestId('facebook-login'),
      line: page.getByTestId('line-login')
    }
  }
  
  async goto() {
    await this.page.goto('/login')
    await expect(this.page.getByTestId('login-form')).toBeVisible()
  }
  
  async login(email: string, password: string) {
    await this.emailInput.fill(email)
    await this.passwordInput.fill(password)
    await this.loginButton.click()
  }
  
  async expectLoginSuccess() {
    // 檢查是否重定向到首頁或用戶儀表板
    await expect(this.page).toHaveURL(/\/(dashboard|home)/)
    await expect(this.page.getByTestId('user-menu')).toBeVisible()
  }
  
  async expectLoginError(message: string) {
    await expect(this.errorMessage).toContainText(message)
  }
  
  async goToRegister() {
    await this.registerLink.click()
    await expect(this.page).toHaveURL('/register')
  }
  
  async goToForgotPassword() {
    await this.forgotPasswordLink.click()
    await expect(this.page).toHaveURL('/forgot-password')
  }
}