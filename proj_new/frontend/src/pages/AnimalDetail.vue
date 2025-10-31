<template>
  <div class="animal-detail-page min-h-screen bg-gray-50 py-8">
    <div class="container mx-auto px-4 max-w-6xl">
      <!-- Loading 狀態 -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-600">載入中...</p>
      </div>

      <!-- 錯誤訊息 -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        {{ error }}
        <div class="mt-4">
          <router-link to="/animals" class="text-blue-600 hover:text-blue-700">
            返回動物列表
          </router-link>
        </div>
      </div>

      <!-- 動物詳情 -->
      <div v-else-if="animal" class="bg-white rounded-lg shadow-lg overflow-hidden">
        <div class="grid md:grid-cols-2 gap-8">
          <!-- 左側：圖片 -->
          <div class="relative">
            <div class="aspect-w-4 aspect-h-3 bg-gray-200">
              <img
                v-if="currentImage"
                :src="currentImage.url"
                :alt="animal.name || '動物照片'"
                class="w-full h-full object-cover"
              />
              <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                <span class="text-8xl">🐾</span>
              </div>
            </div>

            <!-- 圖片縮圖 -->
            <div v-if="animal.images && animal.images.length > 1" class="flex gap-2 p-4 overflow-x-auto">
              <button
                v-for="(image, index) in sortedImages"
                :key="image.animal_image_id"
                @click="currentImageIndex = index"
                class="flex-shrink-0 w-20 h-20 border-2 rounded-md overflow-hidden"
                :class="currentImageIndex === index ? 'border-blue-600' : 'border-gray-300'"
              >
                <img :src="image.url" :alt="`圖片 ${index + 1}`" class="w-full h-full object-cover" />
              </button>
            </div>
          </div>

          <!-- 右側：詳細資訊 -->
          <div class="p-8">
            <!-- 狀態標籤 -->
            <div class="mb-4 flex gap-2">
              <span
                class="inline-block px-3 py-1 text-sm font-semibold rounded-full"
                :class="statusClass"
              >
                {{ statusText }}
              </span>
              <!-- 我的寵物標籤 -->
              <span
                v-if="isMyAnimal"
                class="inline-block px-3 py-1 text-sm font-semibold rounded-full bg-purple-500 text-white"
              >
                👤 我的寵物
              </span>
            </div>

            <!-- 名稱 -->
            <h1 class="text-4xl font-bold text-gray-900 mb-4">
              {{ animal.name || '未命名動物' }}
            </h1>

            <!-- 基本資訊 -->
            <div class="space-y-4 mb-6">
              <h2 class="text-xl font-bold text-gray-900 border-b-2 border-blue-500 pb-2 mb-4">📋 基本資訊</h2>
              
              <div class="flex items-center text-gray-700">
                <span class="w-24 font-medium">物種:</span>
                <span>{{ speciesText }} {{ animal.breed ? `(${animal.breed})` : '' }}</span>
              </div>
              <div v-if="animal.sex" class="flex items-center text-gray-700">
                <span class="w-24 font-medium">性別:</span>
                <span>{{ sexText }}</span>
              </div>
              <div v-if="age" class="flex items-center text-gray-700">
                <span class="w-24 font-medium">年齡:</span>
                <span>{{ age }}</span>
              </div>
            </div>

            <!-- 來源資訊 -->
            <div class="space-y-4 mb-6">
              <h2 class="text-xl font-bold text-gray-900 border-b-2 border-green-500 pb-2 mb-4">🏠 來源資訊</h2>
              
              <div v-if="animal.shelter_id" class="bg-green-50 border border-green-200 rounded-lg p-4">
                <div class="flex items-center gap-2 mb-3">
                  <span class="text-2xl">🏠</span>
                  <span class="text-lg font-semibold text-green-800">收容所</span>
                </div>
                <div v-if="shelterInfo" class="space-y-2 text-sm">
                  <div class="flex items-center gap-2 text-gray-700">
                    <span class="text-green-600">📍</span>
                    <span class="font-medium">地區：</span>
                    <span>{{ shelterInfo.region || '無' }}</span>
                  </div>
                  <div v-if="shelterInfo.address && shelterInfo.address.street" class="flex items-center gap-2 text-gray-700">
                    <span class="text-green-600">🏠</span>
                    <span class="font-medium">地址：</span>
                    <span>{{ formatAddress(shelterInfo.address) }}</span>
                  </div>
                  <div class="flex items-center gap-2 text-gray-700">
                    <span class="text-green-600">🏢</span>
                    <span class="font-medium">機構名稱：</span>
                    <span class="font-semibold text-green-800">{{ shelterInfo.name }}</span>
                  </div>
                </div>
                <div v-else class="text-sm text-gray-500">載入中...</div>
              </div>
              
              <div v-else-if="animal.owner_id" class="bg-green-50 border border-green-200 rounded-lg p-4">
                <div class="flex items-center gap-2 mb-3">
                  <span class="text-2xl">👤</span>
                  <span class="text-lg font-semibold text-green-800">個人送養</span>
                </div>
                <div v-if="ownerInfo" class="space-y-2 text-sm">
                  <div class="flex items-center gap-2 text-gray-700">
                    <span class="text-green-600">📍</span>
                    <span class="font-medium">地區：</span>
                    <span>{{ ownerInfo.region || '無' }}</span>
                  </div>
                  <div class="flex items-center gap-2 text-gray-700">
                    <span class="text-green-600">👤</span>
                    <span class="font-medium">送養人：</span>
                    <span class="font-semibold text-green-800">{{ ownerInfo.username || '匿名' }}</span>
                  </div>
                </div>
                <div v-else class="text-sm text-gray-500">載入中...</div>
              </div>
              
              <div v-else class="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <div class="text-sm text-gray-500">來源資訊不明</div>
              </div>
            </div>

            <!-- 描述 -->
            <div v-if="animal.description" class="mb-6">
              <h2 class="text-xl font-bold text-gray-900 border-b-2 border-purple-500 pb-2 mb-4">💝 關於我</h2>
              <p class="text-gray-700 leading-relaxed whitespace-pre-wrap">{{ animal.description }}</p>
            </div>

            <!-- 醫療摘要 -->
            <div v-if="animal.medical_summary" class="mb-6">
              <h2 class="text-xl font-bold text-gray-900 border-b-2 border-red-500 pb-2 mb-4">❤️ 健康狀況</h2>
              <p class="text-gray-700 leading-relaxed">{{ animal.medical_summary }}</p>
            </div>

            <!-- 詳細醫療記錄 -->
            <div class="mb-6">
              <h2 class="text-xl font-bold text-gray-900 border-b-2 border-orange-500 pb-2 mb-4">🏥 醫療記錄</h2>
              
              <!-- 載入中 -->
              <div v-if="isLoadingMedical" class="text-center py-4">
                <div class="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
                <span class="ml-2 text-gray-600">載入醫療記錄中...</span>
              </div>

              <!-- 錯誤訊息 -->
              <div v-else-if="medicalError" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {{ medicalError }}
              </div>

              <!-- 醫療記錄列表 -->
              <div v-else-if="medicalRecords.length > 0" class="space-y-4">
                <div
                  v-for="record in displayedMedicalRecords"
                  :key="record.medical_record_id"
                  class="bg-gray-50 border border-gray-200 rounded-lg p-4"
                >
                  <div class="flex items-start justify-between mb-2">
                    <div class="flex items-center gap-2">
                      <span
                        class="inline-block px-2 py-1 text-xs font-semibold rounded-full"
                        :class="getMedicalRecordTypeClass(record.record_type)"
                      >
                        {{ getMedicalRecordTypeText(record.record_type) }}
                      </span>
                      <!-- 驗證狀態標籤 -->
                      <span
                        v-if="record.verified"
                        class="inline-block px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800"
                      >
                        ✓ 已驗證
                      </span>
                      <span
                        v-else
                        class="inline-block px-2 py-1 text-xs font-semibold rounded-full bg-orange-100 text-orange-800"
                      >
                        ⚠ 未驗證
                      </span>
                    </div>
                    <span v-if="record.date" class="text-sm text-gray-500">
                      {{ formatMedicalDate(record.date) }}
                    </span>
                  </div>

                  <div class="text-sm text-gray-600 mb-2">
                    <strong>醫療機構:</strong> {{ record.provider || '無' }}
                  </div>

                  <div class="text-sm text-gray-600">
                    <strong>詳細說明:</strong> {{ record.details || '無' }}
                  </div>
                </div>

                <!-- 摺疊/展開按鈕 -->
                <div v-if="shouldShowCollapseButton" class="text-center pt-2">
                  <button
                    @click="showAllMedicalRecords = !showAllMedicalRecords"
                    class="inline-flex items-center gap-2 px-4 py-2 text-sm text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded-lg transition"
                  >
                    <span v-if="showAllMedicalRecords">
                      收起 ({{ sortedMedicalRecords.length - 3 }} 筆)
                    </span>
                    <span v-else>
                      顯示更多 ({{ sortedMedicalRecords.length - 3 }} 筆)
                    </span>
                    <svg
                      class="w-4 h-4 transition-transform"
                      :class="{ 'rotate-180': showAllMedicalRecords }"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- 無醫療記錄訊息 -->
              <div v-else class="text-center py-4 text-gray-500">
                目前沒有醫療記錄
              </div>
            </div>

            <!-- 行動按鈕 -->
            <div class="flex gap-4 mt-8">
              <!-- 已被領養提示 -->
              <div v-if="animal.status === 'ADOPTED'" class="flex-1 bg-blue-50 border-2 border-blue-200 text-blue-800 px-6 py-3 rounded-lg font-semibold text-center">
                💙 此動物已被領養
              </div>
              
              <!-- 有待審核申請提示 -->
              <div v-else-if="animal.has_pending_application && animal.status === 'PUBLISHED'" class="flex-1 bg-orange-50 border-2 border-orange-200 text-orange-800 px-6 py-3 rounded-lg font-semibold text-center">
                📝 此動物目前有待審核的領養申請,請等待審核結果後再提出申請
              </div>
              
              <!-- 我想領養按鈕 (非自己的動物且未被領養且無待審核申請才顯示) -->
              <button
                v-else-if="animal.status === 'PUBLISHED' && isAuthenticated && !isMyAnimal"
                @click="handleApply"
                class="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
              >
                我想領養
              </button>
              <button
                v-else-if="animal.status === 'PUBLISHED' && !isAuthenticated && !isMyAnimal"
                @click="goToLogin"
                class="flex-1 bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
              >
                登入以領養
              </button>

              <!-- 編輯按鈕 (僅 owner 可見) -->
              <button
                v-if="canEdit"
                @click="goToEdit"
                class="px-6 py-3 border-2 border-blue-600 text-blue-600 rounded-lg font-semibold hover:bg-blue-50 transition"
                :class="{ 'flex-1': isMyAnimal || animal.status === 'ADOPTED' }"
              >
                {{ getEditButtonText }}
              </button>
            </div>
          </div>
        </div>

        <!-- 其他資訊區塊 -->
        <div class="px-8 py-6 border-t border-gray-200 bg-gray-50">
          <p class="text-sm text-gray-500">
            發布於: {{ formattedDate }}
          </p>
        </div>
      </div>

      <!-- 返回按鈕 -->
      <div class="mt-6">
        <router-link
          to="/animals"
          class="inline-flex items-center text-blue-600 hover:text-blue-700"
        >
          ← 返回動物列表
        </router-link>
      </div>
    </div>

    <!-- 申請表單對話框 -->
    <div
      v-if="showApplicationModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="closeApplicationModal"
    >
      <div class="bg-white rounded-lg shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4">
          <div class="flex items-center justify-between">
            <h3 class="text-xl font-bold text-gray-900">申請領養</h3>
            <button @click="closeApplicationModal" class="text-gray-400 hover:text-gray-600">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div class="p-6">
          <!-- 錯誤訊息 -->
          <div v-if="applicationError" class="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {{ applicationError }}
          </div>

          <!-- 動物資訊摘要 -->
          <div class="mb-6 p-4 bg-gray-50 rounded-lg">
            <div class="flex items-center gap-4">
              <img
                v-if="currentImage"
                :src="currentImage.url"
                :alt="animal?.name"
                class="w-20 h-20 rounded-lg object-cover"
              />
              <div class="flex-1">
                <h4 class="font-semibold text-gray-900">{{ animal?.name }}</h4>
                <p class="text-sm text-gray-600">{{ speciesText }} {{ animal?.breed ? `· ${animal.breed}` : '' }}</p>
              </div>
            </div>
          </div>

          <!-- 申請表單 -->
          <form @submit.prevent="submitApplication" class="space-y-4">
            <!-- 申請類型 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                申請類型 <span class="text-red-500">*</span>
              </label>
              <select
                v-model="applicationForm.type"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="ADOPTION">領養</option>
                <option value="REHOME">中途送養</option>
              </select>
            </div>

            <!-- 聯絡電話 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                聯絡電話 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="applicationForm.contact_phone"
                type="tel"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="例: 0912345678"
                required
              />
            </div>

            <!-- 聯絡地址 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                聯絡地址 <span class="text-red-500">*</span>
              </label>
              <input
                v-model="applicationForm.contact_address"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="例: 台北市信義區信義路五段7號"
                required
              />
            </div>

            <!-- 職業 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                職業
              </label>
              <input
                v-model="applicationForm.occupation"
                type="text"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="例: 工程師"
              />
            </div>

            <!-- 居住環境 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                居住環境 <span class="text-red-500">*</span>
              </label>
              <select
                v-model="applicationForm.housing_type"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">請選擇</option>
                <option value="公寓">公寓</option>
                <option value="透天厝">透天厝</option>
                <option value="獨棟">獨棟</option>
                <option value="宿舍">宿舍</option>
                <option value="其他">其他</option>
              </select>
            </div>

            <!-- 養寵經驗 -->
            <div class="flex items-center">
              <input
                id="has-experience"
                v-model="applicationForm.has_experience"
                type="checkbox"
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label for="has-experience" class="ml-2 text-sm text-gray-700">
                我有養寵物的經驗
              </label>
            </div>

            <!-- 領養原因 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                領養原因 <span class="text-red-500">*</span>
              </label>
              <textarea
                v-model="applicationForm.reason"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="3"
                placeholder="請說明您想領養的原因..."
                required
              ></textarea>
            </div>

            <!-- 其他備註 -->
            <div>
              <label class="block text-sm font-medium text-gray-700 mb-2">
                其他備註
              </label>
              <textarea
                v-model="applicationForm.notes"
                class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="2"
                placeholder="其他想說明的事項..."
              ></textarea>
            </div>

            <!-- 聯絡資訊說明 -->
            <div class="text-sm text-gray-600 bg-blue-50 border border-blue-200 rounded-md p-3">
              <p class="font-medium text-blue-900 mb-1">📝 申請說明</p>
              <ul class="list-disc list-inside space-y-1">
                <li>請確實填寫以上資料,以利審核</li>
                <li>審核期間可能需要 1-3 個工作天</li>
                <li>審核結果將透過系統通知您</li>
              </ul>
            </div>

            <!-- 確認條款 -->
            <div class="flex items-start">
              <input
                id="agree-terms"
                v-model="agreeTerms"
                type="checkbox"
                class="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label for="agree-terms" class="ml-2 text-sm text-gray-700">
                我同意並理解領養需負起照顧動物的責任,並遵守相關法規
              </label>
            </div>

            <!-- 按鈕 -->
            <div class="flex gap-3 pt-4">
              <button
                type="button"
                @click="closeApplicationModal"
                class="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                :disabled="isSubmitting"
              >
                取消
              </button>
              <button
                type="submit"
                class="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
                :disabled="isSubmitting || !agreeTerms"
              >
                <span v-if="isSubmitting">提交中...</span>
                <span v-else>確認申請</span>
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getAnimal, type Animal } from '@/api/animals'
import { createApplication } from '@/api/applications'
import { getMedicalRecords } from '@/api/medicalRecords'
import { getShelter } from '@/api/shelters'
import { getUser } from '@/api/users'
import { useAuthStore } from '@/stores/auth'
import type { MedicalRecord } from '@/types/models'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const animal = ref<Animal | null>(null)
const isLoading = ref(false)
const error = ref('')
const currentImageIndex = ref(0)

// 來源詳細資訊
const shelterInfo = ref<any>(null)
const ownerInfo = ref<any>(null)

// 醫療記錄相關
const medicalRecords = ref<MedicalRecord[]>([])
const isLoadingMedical = ref(false)
const medicalError = ref('')
const showAllMedicalRecords = ref(false)


// 申請表單相關狀態
const showApplicationModal = ref(false)
const isSubmitting = ref(false)
const applicationError = ref('')
const agreeTerms = ref(false)
const applicationForm = ref({
  type: 'ADOPTION' as 'ADOPTION' | 'REHOME',
  contact_phone: '',
  contact_address: '',
  occupation: '',
  housing_type: '',
  has_experience: false,
  reason: '',
  notes: ''
})

const isAuthenticated = computed(() => authStore.isAuthenticated)

// 排序後的圖片
const sortedImages = computed(() => {
  if (!animal.value?.images) return []
  return [...animal.value.images].sort((a, b) => a.order - b.order)
})

// 當前圖片
const currentImage = computed(() => {
  if (sortedImages.value.length === 0) return null
  return sortedImages.value[currentImageIndex.value] || sortedImages.value[0]
})

// 物種文字
const speciesText = computed(() => {
  const map: Record<string, string> = {
    CAT: '貓',
    DOG: '狗',
  }
  return animal.value?.species ? map[animal.value.species] : '未知'
})

// 性別文字
const sexText = computed(() => {
  const map: Record<string, string> = {
    MALE: '公',
    FEMALE: '母',
    UNKNOWN: '未知',
  }
  return animal.value?.sex ? map[animal.value.sex] : '未知'
})

// 狀態文字
const statusText = computed(() => {
  const map: Record<string, string> = {
    DRAFT: '草稿',
    SUBMITTED: '審核中',
    PUBLISHED: '已上架',
    ADOPTED: '已被領養',
    RETIRED: '已下架',
  }
  return animal.value ? map[animal.value.status] || '未知' : ''
})

// 狀態樣式
const statusClass = computed(() => {
  const map: Record<string, string> = {
    DRAFT: 'bg-gray-100 text-gray-800',
    SUBMITTED: 'bg-yellow-100 text-yellow-800',
    PUBLISHED: 'bg-green-100 text-green-800',
    ADOPTED: 'bg-blue-100 text-blue-800',
    RETIRED: 'bg-red-100 text-red-800',
  }
  return animal.value ? map[animal.value.status] || 'bg-gray-100 text-gray-800' : ''
})

// 計算年齡
const age = computed(() => {
  if (!animal.value?.dob) return null

  const birthDate = new Date(animal.value.dob)
  const today = new Date()
  const years = today.getFullYear() - birthDate.getFullYear()
  const months = today.getMonth() - birthDate.getMonth()

  if (years === 0) {
    return `${months} 個月`
  } else if (months < 0) {
    return `${years - 1} 歲`
  } else {
    return `${years} 歲 ${months} 個月`
  }
})

// 格式化日期
const formattedDate = computed(() => {
  if (!animal.value) return ''
  const date = new Date(animal.value.created_at)
  return date.toLocaleDateString('zh-TW', { year: 'numeric', month: 'long', day: 'numeric' })
})

// 是否可以編輯
const canEdit = computed(() => {
  if (!animal.value || !authStore.user) return false
  
  // 只有動物的建立者(擁有者)可以編輯
  // 管理員不能編輯用戶傳來的送養資料
  return animal.value.created_by === authStore.user.user_id
})

// 是否為我的動物
const isMyAnimal = computed(() => {
  if (!animal.value || !authStore.user) return false
  return animal.value.created_by === authStore.user.user_id
})

// 編輯按鈕文字
const getEditButtonText = computed(() => {
  if (!animal.value || !authStore.user) return '編輯'
  
  const from = route.query.from as string
  
  if (from === 'shelter-animals' && authStore.user.primary_shelter_id) {
    return '返回管理頁面編輯'
  } else if (animal.value.shelter_id && authStore.user.primary_shelter_id === animal.value.shelter_id) {
    return '前往管理頁面編輯'
  } else {
    return '編輯'
  }
})

// 排序後的醫療記錄（最新的在前）
const sortedMedicalRecords = computed(() => {
  return [...medicalRecords.value].sort((a, b) => {
    const dateA = a.date ? new Date(a.date) : new Date(a.created_at)
    const dateB = b.date ? new Date(b.date) : new Date(b.created_at)
    return dateB.getTime() - dateA.getTime()
  })
})

// 顯示的醫療記錄（根據摺疊狀態決定）
const displayedMedicalRecords = computed(() => {
  const records = sortedMedicalRecords.value
  if (showAllMedicalRecords.value || records.length <= 3) {
    return records
  }
  return records.slice(0, 3)
})

// 是否需要顯示摺疊按鈕
const shouldShowCollapseButton = computed(() => {
  return sortedMedicalRecords.value.length > 3
})

// 醫療記錄類型文字
function getMedicalRecordTypeText(type?: string) {
  const map: Record<string, string> = {
    TREATMENT: '治療',
    CHECKUP: '健康檢查',
    VACCINE: '疫苗接種',
    SURGERY: '手術',
    OTHER: '其他'
  }
  return type ? map[type] || '其他' : '其他'
}

// 醫療記錄類型樣式
function getMedicalRecordTypeClass(type?: string) {
  const map: Record<string, string> = {
    TREATMENT: 'bg-blue-100 text-blue-800',
    CHECKUP: 'bg-green-100 text-green-800',
    VACCINE: 'bg-yellow-100 text-yellow-800',
    SURGERY: 'bg-red-100 text-red-800',
    OTHER: 'bg-gray-100 text-gray-800'
  }
  return type ? map[type] || 'bg-gray-100 text-gray-800' : 'bg-gray-100 text-gray-800'
}

// 格式化醫療記錄日期
function formatMedicalDate(dateString: string) {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', { 
    year: 'numeric', 
    month: 'long', 
    day: 'numeric' 
  })
}

// 格式化地址
function formatAddress(address: any) {
  if (!address) return ''
  const parts = []
  if (address.district) parts.push(address.district)
  if (address.street) parts.push(address.street)
  if (address.postal_code) parts.push(`(${address.postal_code})`)
  return parts.join(' ')
}

// 載入動物詳情
async function loadAnimal() {
  const id = parseInt(route.params.id as string)
  if (isNaN(id)) {
    error.value = '無效的動物 ID'
    return
  }

  isLoading.value = true
  error.value = ''

  try {
    animal.value = await getAnimal(id)
    // 載入完動物資料後，載入醫療記錄和來源詳細資訊
    await loadMedicalRecords(id)
    await loadSourceInfo()
  } catch (err: any) {
    console.error('Load animal error:', err)
    if (err.response?.status === 404) {
      error.value = '找不到此動物'
    } else {
      error.value = err.response?.data?.message || '載入失敗'
    }
  } finally {
    isLoading.value = false
  }
}

// 載入來源詳細資訊 (收容所或用戶)
async function loadSourceInfo() {
  if (!animal.value) return

  try {
    if (animal.value.shelter_id) {
      // 載入收容所資訊
      shelterInfo.value = await getShelter(animal.value.shelter_id)
    } else if (animal.value.owner_id) {
      // 載入用戶資訊
      ownerInfo.value = await getUser(animal.value.owner_id)
    }
  } catch (err: any) {
    console.error('Load source info error:', err)
    // 來源資訊載入失敗不影響主要功能，只記錄錯誤
  }
}

// 載入醫療記錄
async function loadMedicalRecords(animalId: number) {
  isLoadingMedical.value = true
  medicalError.value = ''

  try {
    const response = await getMedicalRecords(animalId)
    medicalRecords.value = response.medical_records || []
  } catch (err: any) {
    console.error('Load medical records error:', err)
    
    // 如果是 404 或其他錯誤，不顯示錯誤訊息，只是不顯示醫療記錄
    if (err.response?.status !== 404) {
      medicalError.value = '載入醫療記錄失敗'
    }
    medicalRecords.value = []
  } finally {
    isLoadingMedical.value = false
  }
}

// 處理申請
function handleApply() {
  if (!animal.value) return
  
  // 檢查是否為自己的動物
  if (animal.value.created_by === authStore.user?.user_id) {
    applicationError.value = '您不能申請自己刊登的動物'
    return
  }
  
  // 重置表單
  applicationForm.value = {
    type: 'ADOPTION',
    contact_phone: '',
    contact_address: '',
    occupation: '',
    housing_type: '',
    has_experience: false,
    reason: '',
    notes: ''
  }
  agreeTerms.value = false
  applicationError.value = ''
  showApplicationModal.value = true
}

// 關閉申請對話框
function closeApplicationModal() {
  showApplicationModal.value = false
  applicationError.value = ''
}

// 提交申請
async function submitApplication() {
  if (!animal.value || !agreeTerms.value) return
  
  isSubmitting.value = true
  applicationError.value = ''
  
  try {
    // 生成 Idempotency-Key 避免重複提交
    const idempotencyKey = `apply-${animal.value.animal_id}-${Date.now()}`
    
    await createApplication(
      {
        animal_id: animal.value.animal_id,
        type: applicationForm.value.type,
        contact_phone: applicationForm.value.contact_phone,
        contact_address: applicationForm.value.contact_address,
        occupation: applicationForm.value.occupation,
        housing_type: applicationForm.value.housing_type,
        has_experience: applicationForm.value.has_experience,
        reason: applicationForm.value.reason,
        notes: applicationForm.value.notes
      },
      idempotencyKey
    )
    
    // 成功後關閉對話框並導向我的申請
    showApplicationModal.value = false
    alert('申請已提交!送養人將會審核您的申請。')
    router.push('/my/applications')
  } catch (err: any) {
    console.error('Submit application error:', err)
    if (err.response?.status === 400) {
      applicationError.value = err.response.data.message || err.response.data.error || '申請失敗,請檢查您的資料'
    } else if (err.response?.status === 409 || err.response?.status === 500) {
      // 409 或 500 都可能是重複申請
      const errorMsg = err.response.data.message || err.response.data.error || ''
      if (errorMsg.includes('已對此動物提交申請') || errorMsg.includes('已提交') || errorMsg.includes('重複')) {
        applicationError.value = '您已經對此動物提交過申請了,請前往「我的申請」頁面查看'
        // 3秒後自動跳轉
        setTimeout(() => {
          router.push('/my/applications')
        }, 3000)
      } else {
        applicationError.value = errorMsg || '申請失敗,請稍後再試'
      }
    } else {
      applicationError.value = err.response?.data?.message || err.response?.data?.error || '提交失敗,請稍後再試'
    }
  } finally {
    isSubmitting.value = false
  }
}

// 前往登入
function goToLogin() {
  router.push({ name: 'Login', query: { redirect: route.fullPath } })
}

// 前往編輯
function goToEdit() {
  if (!animal.value) return
  
  // 檢查來源頁面，決定編輯方式
  const from = route.query.from as string
  
  if (from === 'shelter-animals' && authStore.user?.primary_shelter_id) {
    // 如果來自收容所動物管理頁面，返回該頁面
    router.push('/shelter/animals')
  } else if (animal.value.shelter_id && authStore.user?.primary_shelter_id === animal.value.shelter_id) {
    // 如果是收容所動物且用戶是該收容所成員，導向收容所動物管理
    router.push('/shelter/animals')
  } else {
    // 否則導向「我的送養」頁面
    router.push('/my-rehomes')
  }
}

// 初始載入
onMounted(() => {
  loadAnimal()
})
</script>
