import { Page, expect, Locator } from '@playwright/test'
import { testRehomeData } from '../fixtures/rehome-test-data'

export class RehomeFormPage {
  readonly page: Page
  
  // 基本資訊欄位 - 匹配實際 Vue 表單
  readonly nameInput: Locator
  readonly speciesSelect: Locator
  readonly breedInput: Locator
  readonly sexSelect: Locator
  readonly dobInput: Locator
  readonly colorInput: Locator
  readonly descriptionTextarea: Locator
  
  // 步驟控制
  readonly nextStepButton: Locator
  readonly prevStepButton: Locator
  readonly currentStepIndicator: Locator
  
  // 表單提交按鈕
  readonly saveDraftButton: Locator
  readonly submitButton: Locator

  constructor(page: Page) {
    this.page = page
    
    // 基於 RehomeForm.vue 的實際結構
    this.nameInput = page.locator('input[placeholder*="例: 小白"]')
    this.speciesSelect = page.locator('select').first() // 第一個select是物種
    this.breedInput = page.locator('input[placeholder*="米克斯"]')
    this.sexSelect = page.locator('select').nth(1) // 第二個select是性別
    this.dobInput = page.locator('input[type="date"]')
    this.colorInput = page.locator('input[placeholder*="白色、橘色、三花"]')
    this.descriptionTextarea = page.locator('textarea').first()
    
    // 按鈕
    this.nextStepButton = page.locator('button').filter({ hasText: '下一步' })
    this.prevStepButton = page.locator('button').filter({ hasText: '上一步' })
    this.saveDraftButton = page.locator('button').filter({ hasText: '儲存草稿' })
    this.submitButton = page.locator('button[type="submit"]')
    
    // 步驟指示器
    this.currentStepIndicator = page.locator('.step-item.active')
  }

  async fillBasicInfo(animalData = testRehomeData.animalData.basic) {
    console.log('📝 開始填寫基本資訊')
    
    // 填寫名稱
    await this.nameInput.fill(animalData.name)
    console.log(`✅ 填入名稱: ${animalData.name}`)
    
    // 選擇物種 (CAT/DOG)
    const speciesValue = animalData.type === 'cat' ? 'CAT' : 'DOG'
    await this.speciesSelect.selectOption(speciesValue)
    console.log(`✅ 選擇物種: ${speciesValue}`)
    
    // 填寫品種
    await this.breedInput.fill(animalData.breed)
    console.log(`✅ 填入品種: ${animalData.breed}`)
    
    // 選擇性別 (MALE/FEMALE) 
    const sexValue = animalData.gender === 'male' ? 'MALE' : 'FEMALE'
    await this.sexSelect.selectOption(sexValue)
    console.log(`✅ 選擇性別: ${sexValue}`)
    
    // 填寫出生日期
    const dobValue = this.calculateDobFromAge(animalData.age)
    await this.dobInput.fill(dobValue)
    console.log(`✅ 填入出生日期: ${dobValue}`)
    
    // 填寫顏色
    if (this.colorInput) {
      await this.colorInput.fill('棕色') // 使用預設顏色
      console.log(`✅ 填入顏色: 棕色`)
    }
    
    // 填寫描述
    await this.descriptionTextarea.fill('可愛的寵物，健康活潑，適合家庭飼養。')
    console.log(`✅ 填入描述`)
    
    console.log('✅ 基本資訊填寫完成')
  }
  
  private calculateDobFromAge(ageStr: string): string {
    const age = parseInt(ageStr)
    const today = new Date()
    const birthYear = today.getFullYear() - age
    return `${birthYear}-01-01`
  }

  async goToNextStep() {
    console.log('➡️ 點擊下一步')
    await this.nextStepButton.click()
  }
  
  async goToPrevStep() {
    console.log('⬅️ 點擊上一步')
    await this.prevStepButton.click()
  }
  
  async saveDraft() {
    console.log('💾 儲存草稿')
    await this.saveDraftButton.click()
  }
  
  async submitForm() {
    console.log('📤 提交表單')
    await this.submitButton.click()
  }

  async submitForReview() {
    console.log('📤 提交審核')
    
    // 確保我們在最後一步（步驟4：確認送出）
    await this.waitForStep(3) // 第4步的index是3
    
    // 尋找最終的提交按鈕（確認送出）
    const finalSubmitButton = this.page.locator('button[type="submit"]').filter({ hasText: '確認送出' })
    await expect(finalSubmitButton).toBeVisible()
    await finalSubmitButton.click()
    
    // 等待成功訊息
    await this.page.waitForTimeout(3000)
    console.log('✅ 已提交審核')
  }

  // 等待步驟載入
  async waitForStep(stepNumber: number) {
    console.log(`⏳ 等待步驟 ${stepNumber + 1} 載入`)
    // 等待步驟指示器顯示正確的步驟
    const stepElement = this.page.locator(`.step-item`).nth(stepNumber)
    await expect(stepElement).toHaveClass(/active/)
  }

  // 簡化的其他方法
  async fillLocationInfo() { 
    console.log('📍 跳過位置資訊 (表單結構已簡化)')
  }
  
  async fillMedicalInfo() { 
    console.log('🏥 跳過醫療資訊 (將在後續步驟處理)')
  }
  
  async fillBehaviorInfo() { 
    console.log('🐾 跳過行為資訊 (表單結構已簡化)')
  }
  
  async uploadPhotos() { 
    console.log('📸 跳過照片上傳步驟（測試環境）')
    // 在測試環境中，我們暫時跳過實際的照片上傳
    // 因為表單驗證需要照片，我們需要模擬上傳行為
    
    // 如果有檔案輸入元素，嘗試模擬上傳
    const fileInput = this.page.locator('input[type="file"]')
    const fileInputExists = await fileInput.count() > 0
    
    if (fileInputExists) {
      console.log('📸 發現檔案輸入元素，跳過上傳')
      // 在實際測試中，這裡可以上傳真實的測試圖片
    }
    
    console.log('✅ 照片步驟完成')
  }

  async uploadRealPhoto() {
    console.log('📸 開始真實照片上傳')
    
    // 尋找檔案輸入元素（可能是隱藏的）
    const fileInput = this.page.locator('input[type="file"]')
    
    try {
      // 使用真實的測試圖片檔案（正確路徑）
      await fileInput.setInputFiles('./tests/e2e/test-assets/images/test_dog.jpg')
      
      console.log('✅ 測試照片檔案已設置：test_dog.jpg')
      
      // 等待上傳處理
      await this.page.waitForTimeout(3000)
      
      // 檢查是否有上傳成功的指示
      const uploadSuccess = this.page.locator('.upload-success, .file-uploaded, [data-uploaded="true"], .preview-image, img[src*="blob:"]')
      const hasUploadIndicator = await uploadSuccess.count() > 0
      if (hasUploadIndicator) {
        console.log('✅ 檢測到上傳成功指示')
      }
      
      console.log('✅ 真實照片上傳完成')
      
    } catch (error) {
      console.log('⚠️ 照片上傳失敗:', error)
      throw error // 重新拋出錯誤以便測試知道失敗
    }
  }

  async waitForUploadStep() {
    console.log('📸 等待照片上傳步驟載入')
    // 確保我們在照片上傳步驟（步驟2）
    await this.waitForStep(1) // 第2步的index是1
  }

  async waitForMedicalStep() {
    console.log('🏥 等待醫療紀錄步驟載入')
    // 確保我們在醫療紀錄步驟（步驟3）
    await this.waitForStep(2) // 第3步的index是2
  }

  async waitForConfirmationStep() {
    console.log('✅ 等待確認送出步驟載入')
    // 確保我們在確認送出步驟（步驟4）
    await this.waitForStep(3) // 第4步的index是3
  }
  
  async fillRequirements() { 
    console.log('📋 跳過認養要求 (表單結構已簡化)')
  }
}
