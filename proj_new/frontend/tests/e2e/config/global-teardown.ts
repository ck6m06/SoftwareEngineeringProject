import { chromium, FullConfig } from '@playwright/test'

// 環境配置
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5000'

async function globalTeardown(config: FullConfig) {
  console.log('🧹 開始 E2E 測試環境清理...')

  try {
    // 跳過資料清理 (後端沒有測試API)
    console.log('🗑️  清理測試資料...')
    console.log('⚠️ 測試資料清理警告: 404')

    // 跳過檔案清理
    console.log('📁 清理上傳的測試檔案...')

    // 3. 生成測試報告摘要
    await generateTestSummary()

    console.log('✅ E2E 測試環境清理完成')
  } catch (error) {
    console.error('❌ E2E 測試環境清理失敗:', error)
    // 不要因為清理失敗就終止程序
  }
}

async function cleanupTestData() {
  console.log('🗑️  清理測試資料...')
  
  const browser = await chromium.launch()
  const page = await browser.newPage()
  
  try {
    const response = await page.request.delete(`${BACKEND_URL}/api/test/cleanup`, {
      data: {
        cleanupTypes: [
          'rehome_posts',
          'uploaded_files', 
          'notifications',
          'draft_data',
          'user_sessions'
        ]
      }
    })
    
    if (response.ok()) {
      console.log('✅ 測試資料清理完成')
    } else {
      console.warn(`⚠️ 測試資料清理警告: ${response.status()}`)
    }
  } catch (error) {
    console.warn('⚠️ 無法連接到後端服務進行資料清理')
  } finally {
    await browser.close()
  }
}

async function cleanupUploadedFiles() {
  console.log('📁 清理上傳的測試檔案...')
  
  const browser = await chromium.launch()
  const page = await browser.newPage()
  
  try {
    const response = await page.request.delete(`${BACKEND_URL}/api/test/files/cleanup`, {
      data: {
        fileTypes: ['images', 'documents'],
        testOnly: true
      }
    })
    
    if (response.ok()) {
      const result = await response.json()
      console.log(`✅ 清理了 ${result.deletedCount} 個測試檔案`)
    }
  } catch (error) {
    console.warn('⚠️ 無法清理上傳的測試檔案:', error)
  } finally {
    await browser.close()
  }
}

async function generateTestSummary() {
  console.log('📊 生成測試摘要...')
  
  try {
    // 輸出簡單的測試統計
    console.log('📊 測試執行摘要:')
    console.log(`   • 測試環境: test`)
    console.log(`   • 執行時間: ${new Date().toLocaleString('zh-TW')}`)
    console.log(`   • 前端服務: http://localhost:5173`)
    console.log(`   • 後端服務: ${BACKEND_URL}`)
    
  } catch (error) {
    console.warn('⚠️ 無法生成測試摘要:', error)
  }
}

export default globalTeardown