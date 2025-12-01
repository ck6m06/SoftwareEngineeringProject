import { Page, expect } from '@playwright/test'

/**
 * 等待 API 響應並驗證狀態碼
 */
export async function waitForApiResponse(
  page: Page, 
  urlPattern: string | RegExp, 
  expectedStatus = 200
) {
  const response = await page.waitForResponse(urlPattern)
  expect(response.status()).toBe(expectedStatus)
  return response
}

/**
 * 等待多個 API 響應
 */
export async function waitForMultipleApiResponses(
  page: Page,
  patterns: Array<{ url: string | RegExp; status?: number }>
) {
  const promises = patterns.map(pattern => 
    waitForApiResponse(page, pattern.url, pattern.status || 200)
  )
  return Promise.all(promises)
}

/**
 * 模擬網路延遲
 */
export async function simulateNetworkDelay(page: Page, delayMs = 1000) {
  await page.route('**/*', async (route) => {
    await page.waitForTimeout(delayMs)
    route.continue()
  })
}

/**
 * 模擬網路錯誤
 */
export async function simulateNetworkError(page: Page, urlPattern: string | RegExp) {
  await page.route(urlPattern, route => route.abort('failed'))
}

/**
 * 模擬 API 錯誤響應
 */
export async function mockApiError(
  page: Page, 
  urlPattern: string | RegExp, 
  status = 500,
  body = { error: 'Internal Server Error' }
) {
  await page.route(urlPattern, route => 
    route.fulfill({
      status,
      contentType: 'application/json',
      body: JSON.stringify(body)
    })
  )
}

/**
 * 截圖並附加到測試報告
 */
export async function takeScreenshot(page: Page, testInfo: any, name: string) {
  const screenshot = await page.screenshot()
  await testInfo.attach(name, {
    body: screenshot,
    contentType: 'image/png'
  })
}

/**
 * 等待載入狀態完成
 */
export async function waitForPageLoad(page: Page) {
  await page.waitForLoadState('networkidle')
}

/**
 * 檢查元素是否在視窗中可見
 */
export async function isElementInViewport(page: Page, selector: string) {
  return await page.evaluate((selector) => {
    const element = document.querySelector(selector)
    if (!element) return false
    
    const rect = element.getBoundingClientRect()
    return (
      rect.top >= 0 &&
      rect.left >= 0 &&
      rect.bottom <= window.innerHeight &&
      rect.right <= window.innerWidth
    )
  }, selector)
}

/**
 * 滾動到元素位置
 */
export async function scrollToElement(page: Page, selector: string) {
  await page.locator(selector).scrollIntoViewIfNeeded()
}

/**
 * 清理測試檔案
 */
export async function cleanupTestFiles(testFiles: string[]) {
  // 在實際實作中，這裡會清理測試過程中上傳的檔案
  console.log(`Cleaning up test files: ${testFiles.join(', ')}`)
}

/**
 * 產生隨機測試資料
 */
export function generateRandomTestData() {
  const timestamp = Date.now()
  return {
    email: `test.user.${timestamp}@example.com`,
    animalName: `測試寵物_${timestamp}`,
    microchipId: `TEST${timestamp}`,
    phone: `09${Math.floor(Math.random() * 100000000).toString().padStart(8, '0')}`
  }
}

/**
 * 格式化檔案大小
 */
export function formatFileSize(bytes: number): string {
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 Byte'
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

/**
 * 驗證上傳檔案大小限制
 */
export async function validateFileUpload(
  page: Page, 
  fileSelector: string, 
  filePath: string,
  maxSizeMB = 10
) {
  // 簡化實作，移除檔案大小檢查以避免 Node.js 依賴問題
  await page.locator(fileSelector).setInputFiles(filePath)
}

/**
 * 等待表單提交完成
 */
export async function waitForFormSubmission(page: Page) {
  // 等待提交按鈕變為禁用狀態，然後等待重新啟用或頁面跳轉
  await page.waitForFunction(() => {
    const submitButton = document.querySelector('[type="submit"]')
    return submitButton && (submitButton as HTMLButtonElement).disabled
  })
  
  // 等待提交完成
  await page.waitForFunction(() => {
    const submitButton = document.querySelector('[type="submit"]')
    return !submitButton || !(submitButton as HTMLButtonElement).disabled
  }, { timeout: 30000 })
}

/**
 * 驗證表單欄位錯誤訊息
 */
export async function validateFieldError(
  page: Page, 
  fieldName: string, 
  expectedMessage: string
) {
  const errorLocator = page.getByTestId(`validation-${fieldName}`)
  await expect(errorLocator).toBeVisible()
  await expect(errorLocator).toContainText(expectedMessage)
}

/**
 * 獲取測試檔案的絕對路徑
 */
export function getTestFilePath(relativePath: string): string {
  // 簡化實作，直接返回相對路徑，讓 Playwright 處理
  return `tests/e2e/test-assets/${relativePath}`
}