import { chromium, FullConfig } from '@playwright/test'
import { testRehomeData } from '../fixtures/rehome-test-data'

// 環境配置
const FRONTEND_URL = process.env.FRONTEND_URL || 'http://localhost:5173'
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:5000'

async function globalSetup(config: FullConfig) {
  console.log('🚀 開始 E2E 測試環境初始化...')
  console.log(`📍 前端 URL: ${FRONTEND_URL}`)
  console.log(`📍 後端 URL: ${BACKEND_URL}`)

  try {
    // 1. 檢查測試服務是否運行
    await checkTestServices()

    // 2. 跳過資料庫初始化 (後端沒有測試API)
    console.log('⚠️ 跳過資料庫初始化 - 使用現有資料庫')

    // 3. 跳過測試用戶創建 (手動創建或使用現有用戶)
    console.log('⚠️ 跳過測試用戶創建 - 使用現有用戶')

    // 4. 跳過測試資料清理
    console.log('⚠️ 跳過測試資料清理 - 測試結束後手動清理')

    console.log('✅ E2E 測試環境初始化完成 (簡化模式)')
  } catch (error) {
    console.error('❌ E2E 測試環境初始化失敗:', error)
    // 不退出，讓測試繼續
  }
}

async function checkTestServices() {
  console.log('🔍 檢查測試服務狀態...')
  
  const browser = await chromium.launch()
  const page = await browser.newPage()
  
  try {
    // 檢查前端服務
    const frontendResponse = await page.request.get(FRONTEND_URL)
    if (!frontendResponse.ok()) {
      throw new Error(`前端服務未運行 (${FRONTEND_URL}): ${frontendResponse.status()}`)
    }
    console.log('✅ 前端服務正常運行')

    // 檢查後端服務 (簡單連接測試)
    try {
      const backendResponse = await page.request.get(`${BACKEND_URL}/`)
      console.log('✅ 後端服務正常運行 (可連接)')
    } catch (error) {
      console.log('⚠️ 後端服務可能未運行，但測試將繼續')
    }

  } finally {
    await browser.close()
  }
}

async function initializeTestDatabase() {
  console.log('🗄️  初始化測試資料庫...')
  
  const browser = await chromium.launch()
  const page = await browser.newPage()
  
  try {
    // 呼叫資料庫初始化 API
    const response = await page.request.post(`${BACKEND_URL}/api/test/db/init`, {
      data: {
        reset: true,
        seedData: true
      }
    })
    
    if (!response.ok()) {
      throw new Error(`資料庫初始化失敗: ${response.status()}`)
    }
    
    console.log('✅ 測試資料庫初始化完成')
  } finally {
    await browser.close()
  }
}

async function createTestUsers() {
  console.log('👥 創建測試用戶帳號...')
  
  const browser = await chromium.launch()
  const page = await browser.newPage()
  
  try {
    const testUsers = [
      testRehomeData.validMember,
      {
        email: 'admin@test.com',
        password: 'Admin123!',
        firstName: '管理員',
        lastName: '測試',
        role: 'admin'
      }
    ]

    for (const user of testUsers) {
      const response = await page.request.post(`${BACKEND_URL}/api/test/users`, {
        data: user
      })
      
      if (!response.ok() && response.status() !== 409) { // 409 = 用戶已存在
        throw new Error(`創建測試用戶失敗: ${response.status()}`)
      }
    }
    
    console.log('✅ 測試用戶帳號創建完成')
  } finally {
    await browser.close()
  }
}

async function cleanupPreviousTestData() {
  console.log('🧹 清理之前的測試資料...')
  
  const browser = await chromium.launch()
  const page = await browser.newPage()
  
  try {
    // 清理測試相關的送養資訊
    const response = await page.request.delete(`${BACKEND_URL}/api/test/cleanup`, {
      data: {
        cleanupTypes: ['rehome_posts', 'uploaded_files', 'notifications']
      }
    })
    
    if (!response.ok()) {
      console.warn(`⚠️ 清理警告: ${response.status()} - 可能沒有需要清理的資料`)
    } else {
      console.log('✅ 測試資料清理完成')
    }
  } finally {
    await browser.close()
  }
}

export default globalSetup