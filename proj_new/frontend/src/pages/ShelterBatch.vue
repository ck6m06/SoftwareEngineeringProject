<template>
  <div class="shelter-batch">
    <div class="container mx-auto px-4 py-8 max-w-7xl">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">批次送養</h1>
      
      <div class="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
        <div class="flex items-start gap-3">
          <div class="text-2xl">ℹ️</div>
          <div>
            <h2 class="text-lg font-semibold text-blue-900 mb-2">收容所會員功能說明</h2>
            <p class="text-blue-800 mb-2">作為收容所會員，您擁有雙重操作方式：</p>
            <ul class="list-disc list-inside text-blue-800 space-y-1">
              <li><strong>收容所動物管理</strong>：批次管理收容所的動物，支援批次操作</li>
              <li><strong>單次送養</strong>：單隻動物的個別處理（與一般會員相同）</li>
              <li>所有動物都歸屬於收容所，即使是單次新增的也代表機構身份</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- 批次匯入動物資料 -->
      <div class="bg-white rounded-lg shadow p-8 mb-8">
        <div class="flex items-center gap-3 mb-6">
          <div class="text-3xl">⚡</div>
          <h2 class="text-xl font-bold text-gray-900">批次匯入動物資料</h2>
        </div>

        <!-- 說明區 -->
        <div class="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
          <div class="flex items-start gap-3">
            <svg class="h-5 w-5 text-blue-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div class="flex-1">
              <p class="text-sm font-semibold text-blue-900 mb-2">批次匯入支援三種檔案類型:</p>
              <ul class="text-xs text-blue-800 space-y-1 list-disc list-inside">
                <li><strong>動物基本資訊 CSV (必填):</strong> 包含名稱、物種、品種等基本資訊</li>
                <li><strong>醫療記錄 CSV (選填):</strong> 包含多筆醫療記錄,透過動物編號關聯</li>
                <li><strong>照片資料夾 (選填):</strong> 照片檔名格式: 動物編號_順序.jpg (例: 001_1.jpg, 001_2.jpg)</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- CSV 範本下載 -->
        <div class="bg-indigo-50 border border-indigo-200 rounded-lg p-4 mb-6">
          <div class="flex items-start gap-3">
            <svg class="h-5 w-5 text-indigo-600 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div class="flex-1">
              <p class="text-sm text-indigo-800 mb-3"><strong>請先下載範本檔案:</strong></p>
              <div class="flex gap-2 mb-3">
                <button
                  @click="downloadAnimalTemplate"
                  class="text-sm bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded transition"
                >
                  📥 下載動物基本資訊範本
                </button>
                <button
                  @click="downloadMedicalTemplate"
                  class="text-sm bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded transition"
                >
                  📥 下載醫療記錄範本
                </button>
              </div>
              <div class="text-xs text-indigo-700 space-y-1">
                <p><strong>動物基本資訊 CSV 欄位說明:</strong></p>
                <ul class="list-disc list-inside ml-2 mb-2">
                  <li><strong>必填:</strong> animal_code, name, species, breed, sex, dob, color, description</li>
                  <li><strong>animal_code:</strong> 動物編號 (自行編碼,用於關聯照片和醫療記錄,例: 001, 002, A001)</li>
                  <li><strong>species:</strong> CAT 或 DOG</li>
                  <li><strong>sex:</strong> MALE 或 FEMALE</li>
                  <li><strong>dob:</strong> 出生日期，支援多種格式：YYYY-MM-DD、YYYY/MM/DD、DD/MM/YYYY、DD-MM-YYYY</li>
                </ul>
                <p><strong>醫療記錄 CSV 欄位說明:</strong></p>
                <ul class="list-disc list-inside ml-2">
                  <li><strong>必填:</strong> animal_code, record_type, date</li>
                  <li><strong>animal_code:</strong> 對應動物基本資訊的編號</li>
                  <li><strong>record_type:</strong> TREATMENT, CHECKUP, VACCINE, SURGERY, OTHER</li>
                  <li><strong>date:</strong> 醫療日期，支援多種格式：YYYY-MM-DD、YYYY/MM/DD、DD/MM/YYYY、DD-MM-YYYY</li>
                  <li><strong>選填:</strong> provider, details</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- 動物基本資訊 CSV -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">
            <span class="text-red-600">*</span> 動物基本資訊 CSV (必填)
          </label>
          <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-indigo-400 transition">
            <input
              type="file"
              ref="animalCsvInput"
              @change="handleAnimalCsvSelect"
              accept=".csv"
              class="hidden"
            />
            <button
              @click="animalCsvInput?.click()"
              class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition"
              :disabled="isUploading"
            >
              <svg class="h-5 w-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              選擇動物基本資訊 CSV
            </button>
            <p class="text-sm text-gray-500 mt-2">必填: 包含動物的基本資訊</p>
          </div>

          <div v-if="animalCsvFile" class="mt-3 bg-green-50 border border-green-200 rounded-lg p-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <svg class="h-5 w-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-sm font-medium text-gray-900">{{ animalCsvFile.name }}</span>
                <span class="text-xs text-gray-500">({{ formatFileSize(animalCsvFile.size) }})</span>
              </div>
              <button @click="clearAnimalCsv" class="text-red-600 hover:text-red-700" :disabled="isUploading">
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 醫療記錄 CSV (選填) -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">醫療記錄 CSV (選填)</label>
          <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-purple-400 transition">
            <input
              type="file"
              ref="medicalCsvInput"
              @change="handleMedicalCsvSelect"
              accept=".csv"
              class="hidden"
            />
            <button
              @click="medicalCsvInput?.click()"
              class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition"
              :disabled="isUploading"
            >
              <svg class="h-5 w-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              選擇醫療記錄 CSV
            </button>
            <p class="text-sm text-gray-500 mt-2">選填: 可包含多筆醫療記錄</p>
          </div>

          <div v-if="medicalCsvFile" class="mt-3 bg-purple-50 border border-purple-200 rounded-lg p-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <svg class="h-5 w-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span class="text-sm font-medium text-gray-900">{{ medicalCsvFile.name }}</span>
                <span class="text-xs text-gray-500">({{ formatFileSize(medicalCsvFile.size) }})</span>
              </div>
              <button @click="clearMedicalCsv" class="text-red-600 hover:text-red-700" :disabled="isUploading">
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- 照片批次上傳 (選填) -->
        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">動物照片 (選填)</label>
          <div class="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-green-400 transition">
            <input
              type="file"
              ref="photosInput"
              @change="handlePhotosSelect"
              accept="image/*"
              multiple
              class="hidden"
            />
            <button
              @click="photosInput?.click()"
              class="inline-flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition"
              :disabled="isUploading"
            >
              <svg class="h-5 w-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              選擇動物照片
            </button>
            <p class="text-sm text-gray-500 mt-2">選填: 檔名格式 動物編號_順序.jpg (例: 001_1.jpg)</p>
          </div>

          <div v-if="photoFiles.length > 0" class="mt-3 bg-green-50 border border-green-200 rounded-lg p-3">
            <div class="flex items-center justify-between mb-2">
              <span class="text-sm font-medium text-gray-900">已選擇 {{ photoFiles.length }} 張照片</span>
              <button @click="clearPhotos" class="text-red-600 hover:text-red-700 text-sm" :disabled="isUploading">
                清除全部
              </button>
            </div>
            <div class="grid grid-cols-4 gap-2 max-h-40 overflow-y-auto">
              <div v-for="(file, index) in photoFiles.slice(0, 12)" :key="index" class="relative">
                <img :src="getPhotoPreview(file)" class="w-full h-20 object-cover rounded" />
                <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-50 text-white text-xs px-1 truncate">
                  {{ file.name }}
                </div>
              </div>
            </div>
            <p v-if="photoFiles.length > 12" class="text-xs text-gray-600 mt-2">
              還有 {{ photoFiles.length - 12 }} 張照片未顯示
            </p>
          </div>
        </div>

        <!-- 錯誤訊息 -->
        <div v-if="errorMessage" class="mb-4 bg-red-50 border border-red-200 rounded-lg p-4">
          <p class="text-sm text-red-800">{{ errorMessage }}</p>
        </div>

        <!-- 上傳按鈕 -->
        <button
          @click="uploadBatch"
          :disabled="!animalCsvFile || isUploading"
          class="w-full bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white py-3 px-6 rounded-lg font-medium transition"
        >
          {{ isUploading ? '上傳中...' : '開始批次匯入' }}
        </button>
      </div>

      <!-- 匯入歷史記錄 -->
      <div class="bg-white rounded-lg shadow p-8">
        <div class="flex items-center justify-between mb-6">
          <h2 class="text-xl font-bold text-gray-900">匯入歷史記錄</h2>
          <button
            @click="loadJobs"
            class="text-sm text-indigo-600 hover:text-indigo-700 transition"
            :disabled="loadingJobs"
          >
            🔄 重新整理
          </button>
        </div>

        <!-- 載入中 -->
        <div v-if="loadingJobs" class="text-center py-8">
          <svg class="animate-spin h-8 w-8 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>

        <!-- 記錄列表 -->
        <div v-else-if="jobs.length > 0" class="space-y-4">
          <div
            v-for="job in jobs"
            :key="job.job_id"
            class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
          >
            <div class="flex items-start justify-between mb-3">
              <div>
                <div class="flex items-center gap-2 mb-1">
                  <span class="font-medium text-gray-900">批次匯入任務 #{{ job.job_id }}</span>
                  <span
                    :class="{
                      'bg-yellow-100 text-yellow-800': job.status === 'PENDING',
                      'bg-blue-100 text-blue-800': job.status === 'RUNNING',
                      'bg-green-100 text-green-800': job.status === 'SUCCEEDED',
                      'bg-red-100 text-red-800': job.status === 'FAILED'
                    }"
                    class="px-2 py-0.5 rounded text-xs font-medium"
                  >
                    {{ getJobStatusText(job.status) }}
                  </span>
                </div>
                <p class="text-sm text-gray-500">建立時間: {{ formatDate(job.created_at) }}</p>
              </div>
            </div>

            <!-- 進度資訊 -->
            <div v-if="job.result_summary" class="bg-gray-50 rounded p-3 text-sm">
              <div v-if="job.status === 'SUCCEEDED'" class="space-y-1">
                <p class="text-green-800"><strong>✓ 匯入成功</strong></p>
                <p class="text-gray-700">總計: {{ job.result_summary.total_rows }} 筆</p>
                <p class="text-gray-700">成功: {{ job.result_summary.success_count }} 筆</p>
                <p class="text-gray-700">失敗: {{ job.result_summary.failed_count }} 筆</p>
              </div>
              <div v-else-if="job.status === 'FAILED'" class="text-red-800">
                <p><strong>✗ 匯入失敗</strong></p>
                <p class="text-sm mt-1">{{ job.result_summary.error }}</p>
              </div>
              <div v-else-if="job.status === 'RUNNING'" class="text-blue-800">
                <p>⏳ 正在處理中...</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 空狀態 -->
        <div v-else class="text-center py-8 text-gray-500">
          <svg class="h-12 w-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p>尚無匯入記錄</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getJobs } from '@/api/jobs'
import type { Job } from '@/types/models'
import api from '@/api/client'

const router = useRouter()
const authStore = useAuthStore()

// 檔案輸入 refs
const animalCsvInput = ref<HTMLInputElement>()
const medicalCsvInput = ref<HTMLInputElement>()
const photosInput = ref<HTMLInputElement>()

// 檔案狀態
const animalCsvFile = ref<File | null>(null)
const medicalCsvFile = ref<File | null>(null)
const photoFiles = ref<File[]>([])

const isUploading = ref(false)
const errorMessage = ref('')
const jobs = ref<Job[]>([])
const loadingJobs = ref(false)

onMounted(() => {
  loadJobs()
})

// ===== 動物基本資訊 CSV =====
function handleAnimalCsvSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    
    if (!file.name.endsWith('.csv')) {
      errorMessage.value = '請選擇 CSV 檔案'
      return
    }
    
    if (file.size > 10 * 1024 * 1024) {
      errorMessage.value = '檔案大小不能超過 10MB'
      return
    }
    
    animalCsvFile.value = file
    errorMessage.value = ''
  }
}

function clearAnimalCsv() {
  animalCsvFile.value = null
  if (animalCsvInput.value) {
    animalCsvInput.value.value = ''
  }
}

// ===== 醫療記錄 CSV =====
function handleMedicalCsvSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    const file = target.files[0]
    
    if (!file.name.endsWith('.csv')) {
      errorMessage.value = '請選擇 CSV 檔案'
      return
    }
    
    if (file.size > 10 * 1024 * 1024) {
      errorMessage.value = '檔案大小不能超過 10MB'
      return
    }
    
    medicalCsvFile.value = file
    errorMessage.value = ''
  }
}

function clearMedicalCsv() {
  medicalCsvFile.value = null
  if (medicalCsvInput.value) {
    medicalCsvInput.value.value = ''
  }
}

// ===== 照片選擇 =====
function handlePhotosSelect(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    const files = Array.from(target.files)
    
    // 驗證檔案類型
    const invalidFiles = files.filter(f => !f.type.startsWith('image/'))
    if (invalidFiles.length > 0) {
      errorMessage.value = `有 ${invalidFiles.length} 個檔案不是圖片格式`
      return
    }
    
    // 驗證檔案大小
    const oversizeFiles = files.filter(f => f.size > 5 * 1024 * 1024)
    if (oversizeFiles.length > 0) {
      errorMessage.value = `有 ${oversizeFiles.length} 個檔案超過 5MB`
      return
    }
    
    photoFiles.value = files
    errorMessage.value = ''
  }
}

function clearPhotos() {
  photoFiles.value = []
  if (photosInput.value) {
    photosInput.value.value = ''
  }
}

function getPhotoPreview(file: File): string {
  return URL.createObjectURL(file)
}

// ===== 批次上傳 =====
async function uploadBatch() {
  if (!animalCsvFile.value) {
    errorMessage.value = '請先選擇動物基本資訊 CSV 檔案'
    return
  }
  
  if (!authStore.user?.primary_shelter_id) {
    errorMessage.value = '您不是收容所會員,無法使用批次匯入功能'
    return
  }
  
  isUploading.value = true
  errorMessage.value = ''
  
  try {
    // Debug: 檢查檔案物件
    console.log('[DEBUG] animalCsvFile:', animalCsvFile.value)
    console.log('[DEBUG] animalCsvFile type:', animalCsvFile.value?.constructor.name)
    console.log('[DEBUG] medicalCsvFile:', medicalCsvFile.value)
    console.log('[DEBUG] photoFiles count:', photoFiles.value.length)
    
    // 使用 FormData 上傳多個檔案
    const formData = new FormData()
    formData.append('animal_csv', animalCsvFile.value)
    
    if (medicalCsvFile.value) {
      formData.append('medical_csv', medicalCsvFile.value)
    }
    
    // 上傳所有照片
    photoFiles.value.forEach((file) => {
      formData.append('photos', file)
    })
    
    // Debug: 檢查 FormData 內容
    console.log('[DEBUG] FormData entries:')
    for (let pair of formData.entries()) {
      console.log(`  ${pair[0]}:`, pair[1])
    }
    
    // FormData 會被 interceptor 自動處理,移除預設的 Content-Type
    const response = await api.post(
      `/shelters/${authStore.user.primary_shelter_id}/animals/batch`,
      formData
    )
    
        alert(`批次匯入已加入隊列!\n任務 ID: ${response.data.job_id}\n\n請前往「動物管理」查看匯入的動物並進行狀態管理`)
        
        // 清空所有檔案選擇
        clearAnimalCsv()
        clearMedicalCsv()
        clearPhotos()
        
        // 重新載入任務列表
        await loadJobs()
        
        // 3秒後跳轉到動物管理頁面
        setTimeout(() => {
          router.push('/shelter/animals')
        }, 3000)  } catch (err: any) {
    console.error('Upload error:', err)
    console.error('Error response:', err.response?.data)
    console.error('Error status:', err.response?.status)
    console.error('Error message:', err.response?.data?.message)
    errorMessage.value = err.response?.data?.message || '上傳失敗,請稍後再試'
  } finally {
    isUploading.value = false
  }
}

// ===== Jobs 管理 =====
async function loadJobs() {
  loadingJobs.value = true
  
  try {
    const response = await getJobs({
      type: 'import_animals',
      per_page: 10
    })
    jobs.value = response.jobs
  } catch (err) {
    console.error('Failed to load jobs:', err)
  } finally {
    loadingJobs.value = false
  }
}

// ===== 範本下載 =====
function downloadAnimalTemplate() {
  const csvContent = `animal_code,name,species,breed,sex,dob,color,description
001,Buddy,DOG,Mixed Breed,MALE,2023-01-15,White,Friendly and energetic dog suitable for families
002,Whiskers,CAT,Orange Tabby,FEMALE,2024-03-20,Orange,Quiet and gentle cat who loves sunbathing
003,Max,DOG,Labrador,MALE,2022-06-10,Black,Gentle and friendly large dog suitable for experienced owners
004,Luna,CAT,Mixed Breed,FEMALE,2023-08-05,Calico,Affectionate cat who loves attention and is litter trained`
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = 'animals_template.csv'
  link.click()
}

function downloadMedicalTemplate() {
  const csvContent = `animal_code,record_type,date,provider,details
001,VACCINE,2024-09-15,City Animal Hospital,Rabies vaccination completed
001,SURGERY,2024/03/10,Love & Care Veterinary,Neutering surgery recovery excellent
002,CHECKUP,01/10/2024,Pet Health Center,Annual health check normal no abnormalities
003,VACCINE,20-08-2024,Animal Shelter Clinic,Three-in-one vaccine administered
003,TREATMENT,2024-07-15,Animal Hospital,Skin treatment fully recovered`
  
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = 'medical_records_template.csv'
  link.click()
}

// ===== 工具函數 =====
function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString('zh-TW')
}

function getJobStatusText(status: string): string {
  const statusMap: Record<string, string> = {
    'PENDING': '等待中',
    'RUNNING': '處理中',
    'SUCCEEDED': '成功',
    'FAILED': '失敗'
  }
  return statusMap[status] || status
}
</script>
