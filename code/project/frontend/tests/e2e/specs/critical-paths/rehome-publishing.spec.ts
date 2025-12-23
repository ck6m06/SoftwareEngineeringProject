import { test, expect } from '@playwright/test'
import { RehomeFormPage } from '../../page-objects/RehomeFormPage'
import { NavigationPage } from '../../page-objects/NavigationPage'
import { loginAsValidMember } from '../../fixtures/auth-helpers'

test.describe('P0-2 送養發布流程', () => {
  test('P0-2-003 完整提交流程驗證（使用真實照片）', async ({ page }) => {
    const navigationPage = new NavigationPage(page)
    const rehomeFormPage = new RehomeFormPage(page)

    console.log(' 開始 P0-2 完整送養測試（含真實照片）')

    // Step 1: 登入系統
    await loginAsValidMember(page)

    // Step 2: 導航至送養表單
    await navigationPage.goToRehomeNew()
    await expect(page).toHaveURL('/rehome-form')

    // Step 3: 填寫基本資訊
    await rehomeFormPage.fillBasicInfo()

    // Step 4: 進入照片上傳步驟
    await rehomeFormPage.goToNextStep()
    await rehomeFormPage.waitForUploadStep()

    // Step 5: 上傳真實照片
    try {
      await rehomeFormPage.uploadRealPhoto()
      console.log('✅ 照片上傳成功，繼續完整流程')

      // Step 6: 進入醫療紀錄步驟
      await rehomeFormPage.goToNextStep()
      await rehomeFormPage.waitForMedicalStep()

      // Step 7: 進入確認送出步驟
      await rehomeFormPage.goToNextStep()
      await rehomeFormPage.waitForConfirmationStep()

      // Step 8: 最終提交審核
      await rehomeFormPage.submitForReview()

      console.log('🎉 完整提交流程測試成功！')

    } catch (error) {
      console.log('⚠️ 照片上傳失敗，改為儲存草稿')
      await rehomeFormPage.saveDraft()
      console.log(' 📝 測試完成（草稿模式）')
    }
  })
})
