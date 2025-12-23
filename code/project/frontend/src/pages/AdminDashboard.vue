<template>
  <div class="admin-dashboard min-h-screen bg-gray-50 py-8">
    <div class="container mx-auto px-4 max-w-7xl">
      <h1 class="text-3xl font-bold text-gray-900 mb-8">管理後台</h1>

      <!-- 統計卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600">待審核動物</p>
              <p class="text-2xl font-bold text-orange-600">{{ stats.submitted }}</p>
            </div>
            <div class="text-orange-500 text-3xl">⏳</div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600">已發布動物</p>
              <p class="text-2xl font-bold text-green-600">{{ stats.published }}</p>
            </div>
            <div class="text-green-500 text-3xl">✓</div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600">草稿動物</p>
              <p class="text-2xl font-bold text-gray-600">{{ stats.draft }}</p>
            </div>
            <div class="text-gray-500 text-3xl">📝</div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-sm text-gray-600">已下架動物</p>
              <p class="text-2xl font-bold text-red-600">{{ stats.retired }}</p>
            </div>
            <div class="text-red-500 text-3xl">✗</div>
          </div>
        </div>
      </div>

      <!-- 快速連結 -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <button
          @click="router.push('/medical-records')"
          class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition text-left"
        >
          <div class="flex items-center gap-3">
            <div class="text-3xl">🏥</div>
            <div>
              <p class="font-semibold text-gray-900">醫療記錄管理</p>
              <p class="text-sm text-gray-600">查看與驗證醫療記錄</p>
            </div>
          </div>
        </button>

        <button
          @click="router.push('/jobs')"
          class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition text-left"
        >
          <div class="flex items-center gap-3">
            <div class="text-3xl">📊</div>
            <div>
              <p class="font-semibold text-gray-900">任務狀態</p>
              <p class="text-sm text-gray-600">查看背景任務執行狀態</p>
            </div>
          </div>
        </button>

        <button
          @click="router.push('/notifications')"
          class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition text-left"
        >
          <div class="flex items-center gap-3">
            <div class="text-3xl">🔔</div>
            <div>
              <p class="font-semibold text-gray-900">通知中心</p>
              <p class="text-sm text-gray-600">查看所有通知</p>
            </div>
          </div>
        </button>

        <button
          @click="router.push('/audit-logs')"
          class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition text-left"
        >
          <div class="flex items-center gap-3">
            <div class="text-3xl">📋</div>
            <div>
              <p class="font-semibold text-gray-900">審計日誌</p>
              <p class="text-sm text-gray-600">查看系統操作記錄</p>
            </div>
          </div>
        </button>

        <button
          @click="router.push('/admin/users')"
          class="bg-white rounded-lg shadow p-4 hover:shadow-lg transition text-left"
        >
          <div class="flex items-center gap-3">
            <div class="text-3xl">👥</div>
            <div>
              <p class="font-semibold text-gray-900">用戶管理</p>
              <p class="text-sm text-gray-600">管理系統用戶與權限</p>
            </div>
          </div>
        </button>
      </div>

      <!-- 狀態篩選 -->
      <div class="bg-white rounded-lg shadow mb-6">
        <div class="p-4 border-b border-gray-200">
          <div class="flex gap-2">
            <button
              v-for="status in statusOptions"
              :key="status.value"
              @click="currentStatus = status.value; loadAnimals()"
              class="px-4 py-2 rounded-lg font-medium transition"
              :class="currentStatus === status.value 
                ? 'bg-blue-600 text-white' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'"
            >
              {{ status.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- 批次操作區 -->
      <div v-if="canShowBatchOperations" class="bg-white rounded-lg shadow mb-6 p-4">
        <div class="flex justify-between items-center flex-wrap gap-4">
          <div class="flex items-center gap-4">
            <span class="text-sm font-medium text-gray-700">
              <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              已選擇 {{ selectedAnimals.length }} 隻動物
            </span>
            <div class="flex gap-2">
              <button @click="clearSelection" class="text-sm text-gray-500 hover:text-gray-700">清除選擇</button>
              <button @click="toggleSelectAll" class="text-sm text-blue-600 hover:text-blue-700">
                {{ isAllSelected ? '取消全選' : '全選' }}
              </button>
            </div>
          </div>
          
          <div class="flex gap-2">
            <button
              v-if="currentStatus === 'SUBMITTED'"
              @click="batchOperation('publish')"
              :disabled="batchProcessing || selectedAnimals.length === 0"
              class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ batchProcessing ? '處理中...' : '批次核准發布' }}
            </button>
            
            <button
              v-if="currentStatus === 'SUBMITTED'"
              @click="openBatchRejectModal"
              :disabled="batchProcessing || selectedAnimals.length === 0"
              class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ batchProcessing ? '處理中...' : '批次拒絕' }}
            </button>

            <button
              v-if="currentStatus === 'PUBLISHED'"
              @click="batchOperation('retire')"
              :disabled="batchProcessing || selectedAnimals.length === 0"
              class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              {{ batchProcessing ? '處理中...' : '批次下架' }}
            </button>
          </div>
        </div>
        
        <!-- 已選動物預覽 -->
        <div v-if="selectedAnimals.length > 0 && selectedAnimals.length <= 5" class="mt-4 pt-4 border-t border-gray-200">
          <div class="text-sm text-gray-600 mb-2">已選中的動物：</div>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="animalId in selectedAnimals.slice(0, 5)"
              :key="animalId"
              class="inline-flex items-center gap-2 px-3 py-1 bg-blue-50 border border-blue-200 rounded-full text-sm"
            >
              <span>{{ getAnimalName(animalId) }}</span>
              <button @click="toggleAnimal(animalId)" class="text-blue-600 hover:text-blue-800">×</button>
            </div>
            <div v-if="selectedAnimals.length > 5" class="px-3 py-1 bg-gray-100 rounded-full text-sm text-gray-600">
              還有 {{ selectedAnimals.length - 5 }} 隻...
            </div>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-600">載入中...</p>
      </div>

      <!-- 動物列表 -->
      <div v-else-if="animals.length > 0" class="space-y-4">
        <!-- 列表標題和全選控制 -->
        <div v-if="currentStatus === 'SUBMITTED' || currentStatus === 'PUBLISHED'" class="bg-white rounded-lg shadow p-4">
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-3">
              <input
                type="checkbox"
                :checked="isAllSelected"
                :indeterminate="selectedAnimals.length > 0 && !isAllSelected"
                @change="toggleSelectAll"
                class="w-4 h-4 rounded border-gray-300 accent-blue-600"
              />
              <label @click="toggleSelectAll" class="text-sm font-medium text-gray-700 cursor-pointer">
                {{ isAllSelected ? '取消全選' : selectedAnimals.length > 0 ? '全選' : '全選' }}
              </label>
            </div>
            <div v-if="selectedAnimals.length > 0" class="text-sm text-blue-600 font-medium">
              已選 {{ selectedAnimals.length }}/{{ animals.length }}
            </div>
          </div>
        </div>

        <div
          v-for="animal in animals"
          :key="animal.animal_id"
          class="bg-white rounded-lg shadow hover:shadow-lg transition p-6"
          :class="{ 'ring-2 ring-blue-500 bg-blue-50': selectedAnimals.includes(animal.animal_id) }"
        >
          <div class="flex gap-6">
            <!-- 選擇框 -->
            <div v-if="currentStatus === 'SUBMITTED' || currentStatus === 'PUBLISHED'" class="flex-shrink-0 pt-2">
              <input
                type="checkbox"
                :checked="selectedAnimals.includes(animal.animal_id)"
                @change="toggleAnimal(animal.animal_id)"
                class="w-5 h-5 rounded border-gray-300 accent-blue-600"
              />
            </div>
            <!-- 圖片 -->
            <div class="flex-shrink-0">
              <img
                v-if="animal.images && animal.images.length > 0"
                :src="animal.images[0].url"
                :alt="animal.name"
                class="w-32 h-32 rounded-lg object-cover"
              />
              <div v-else class="w-32 h-32 rounded-lg bg-gray-200 flex items-center justify-center">
                <span class="text-4xl">🐾</span>
              </div>
            </div>

            <!-- 資訊 -->
            <div class="flex-1">
              <div class="flex items-start justify-between mb-3">
                <div>
                  <h3 class="text-xl font-bold text-gray-900 mb-1">{{ animal.name || '未命名' }}</h3>
                  <div class="flex flex-wrap items-center gap-2 text-sm">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full bg-blue-100 text-blue-800 font-medium">
                      {{ getSpeciesText(animal.species || '') }}
                    </span>
                    <span v-if="animal.breed" class="inline-flex items-center px-2.5 py-0.5 rounded-full bg-purple-100 text-purple-800 font-medium">
                      {{ animal.breed }}
                    </span>
                    <span v-if="animal.sex" class="inline-flex items-center px-2.5 py-0.5 rounded-full bg-pink-100 text-pink-800 font-medium">
                      {{ getSexText(animal.sex) }}
                    </span>
                    <span v-if="animal.color" class="inline-flex items-center px-2.5 py-0.5 rounded-full bg-gray-100 text-gray-800 font-medium">
                      {{ animal.color }}
                    </span>
                    <span v-if="animal.age !== null && animal.age !== undefined" class="inline-flex items-center px-2.5 py-0.5 rounded-full bg-green-100 text-green-800 font-medium">
                      {{ animal.age }} 歲
                    </span>
                  </div>
                </div>
                <span
                  class="px-3 py-1 text-sm font-semibold rounded-full whitespace-nowrap"
                  :class="getStatusClass(animal.status)"
                >
                  {{ getStatusText(animal.status) }}
                </span>
              </div>

              <p v-if="animal.description" class="text-gray-700 mb-3 line-clamp-2">
                {{ animal.description }}
              </p>

              <!-- 詳細資訊網格 -->
              <div class="grid grid-cols-2 gap-x-6 gap-y-2 text-sm mb-4 bg-gray-50 p-3 rounded-lg">
                <div class="flex items-center">
                  <span class="text-gray-500 font-medium w-20">動物 ID:</span>
                  <span class="text-gray-900">{{ animal.animal_id }}</span>
                </div>
                <div class="flex items-center">
                  <span class="text-gray-500 font-medium w-20">出生日期:</span>
                  <span class="text-gray-900">{{ animal.dob ? formatDateOnly(animal.dob) : '未提供' }}</span>
                </div>
                <div class="flex items-center">
                  <span class="text-gray-500 font-medium w-20">送養者:</span>
                  <span class="text-gray-900">ID {{ animal.owner_id || animal.created_by }}</span>
                </div>
                <div class="flex items-center">
                  <span class="text-gray-500 font-medium w-20">收容所:</span>
                  <span class="text-gray-900">{{ animal.shelter_id ? `ID ${animal.shelter_id}` : '個人送養' }}</span>
                </div>
                <div class="flex items-center">
                  <span class="text-gray-500 font-medium w-20">建立時間:</span>
                  <span class="text-gray-900">{{ formatDate(animal.created_at) }}</span>
                </div>
                <div class="flex items-center">
                  <span class="text-gray-500 font-medium w-20">更新時間:</span>
                  <span class="text-gray-900">{{ formatDate(animal.updated_at) }}</span>
                </div>
                <div v-if="animal.rejection_reason" class="col-span-2">
                  <span class="text-red-500 font-medium">拒絕原因:</span>
                  <span class="text-red-700 ml-2">{{ animal.rejection_reason }}</span>
                </div>
                <div v-if="animal.has_pending_application" class="col-span-2">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full bg-yellow-100 text-yellow-800 font-medium text-xs">
                    ⚠️ 有待審核的領養申請
                  </span>
                </div>
              </div>

              <!-- 操作按鈕 -->
              <div class="flex gap-2">
                <button
                  v-if="animal.status === 'SUBMITTED'"
                  @click="publishAnimal(animal.animal_id)"
                  class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium"
                  :disabled="isProcessing"
                >
                  ✓ 核准發布
                </button>

                <button
                  v-if="animal.status === 'SUBMITTED'"
                  @click="openRejectModal(animal.animal_id)"
                  class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium"
                  :disabled="isProcessing"
                >
                  ✗ 拒絕
                </button>

                <button
                  v-if="animal.status === 'PUBLISHED'"
                  @click="retireAnimal(animal.animal_id)"
                  class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium"
                  :disabled="isProcessing"
                >
                  下架
                </button>

                <button
                  @click="viewDetail(animal.animal_id)"
                  class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
                >
                  查看詳情
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空狀態 -->
      <div v-else class="bg-white rounded-lg shadow p-12 text-center">
        <div class="text-6xl mb-4">📭</div>
        <p class="text-xl text-gray-600">目前沒有 {{ getCurrentStatusLabel() }} 的動物</p>
      </div>

      <!-- 分頁 -->
      <div v-if="pagination.pages > 1" class="mt-6 flex justify-center gap-2">
        <button
          @click="changePage(pagination.page - 1)"
          :disabled="pagination.page === 1"
          class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          上一頁
        </button>
        
        <span class="px-4 py-2 text-gray-700">
          第 {{ pagination.page }} / {{ pagination.pages }} 頁
        </span>
        
        <button
          @click="changePage(pagination.page + 1)"
          :disabled="pagination.page >= pagination.pages"
          class="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          下一頁
        </button>
      </div>
    </div>

    <!-- 拒絕原因 Modal (問題4、問題5) -->
    <div v-if="showRejectModal" class="modal-overlay" @click.self="closeRejectModal">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">
            {{ isBatchReject ? `批次拒絕 ${selectedAnimals.length} 隻動物` : '拒絕批准動物上架' }}
          </h2>
          <button type="button" @click="closeRejectModal" class="modal-close">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="modal-body">
          <div v-if="isBatchReject" class="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <p class="text-sm text-blue-800">
              <strong>批次操作：</strong>將對以下 {{ selectedAnimals.length }} 隻動物套用相同的拒絕原因
            </p>
            <div class="mt-2 flex flex-wrap gap-1">
              <span
                v-for="animalId in selectedAnimals.slice(0, 3)"
                :key="animalId"
                class="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
              >
                {{ getAnimalName(animalId) }}
              </span>
              <span v-if="selectedAnimals.length > 3" class="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                +{{ selectedAnimals.length - 3 }} 隻
              </span>
            </div>
          </div>

          <div class="mb-4">
            <label for="rejection-reason" class="form-label required">拒絕原因</label>
            <textarea 
              id="rejection-reason" 
              v-model="rejectionReason" 
              class="form-textarea w-full" 
              rows="5"
              placeholder="請詳細說明拒絕的原因,這將通知給送養者..."
              required
            ></textarea>
            <p class="text-sm text-gray-500 mt-1">送養者將收到此訊息,請提供建設性的反饋</p>
          </div>

          <div class="alert alert-warning mb-4">
            <p class="text-sm">
              <strong>注意:</strong> 
              {{ isBatchReject 
                ? `拒絕後這 ${selectedAnimals.length} 隻動物狀態將改為草稿，送養者需修正後重新提交。`
                : '拒絕後動物狀態將改為草稿,送養者需修正後重新提交。'
              }}
            </p>
          </div>

          <div class="form-actions flex justify-end gap-2">
            <button type="button" @click="closeRejectModal" class="btn-secondary">取消</button>
            <button 
              type="button" 
              @click="confirmReject" 
              class="btn-reject"
              :disabled="isProcessing || batchProcessing || !rejectionReason.trim()"
            >
              {{ isProcessing || batchProcessing ? '處理中...' : (isBatchReject ? '確認批次拒絕' : '確認拒絕') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getAnimals, publishAnimal as publishAnimalAPI, retireAnimal as retireAnimalAPI, rejectAnimal as rejectAnimalAPI, type Animal } from '@/api/animals'

const router = useRouter()

const animals = ref<Animal[]>([])
const isLoading = ref(false)
const isProcessing = ref(false)
const batchProcessing = ref(false)
const currentStatus = ref('SUBMITTED')
const selectedAnimals = ref<number[]>([])
const stats = ref({
  draft: 0,
  submitted: 0,
  published: 0,
  retired: 0
})

// 拒絕 Modal 狀態
const showRejectModal = ref(false)
const rejectingAnimalId = ref<number | null>(null)
const rejectionReason = ref('')
const isBatchReject = ref(false)

const pagination = ref({
  page: 1,
  per_page: 20,
  pages: 1,
  total: 0
})

const statusOptions = [
  { value: 'SUBMITTED', label: '待審核' },
  { value: 'PUBLISHED', label: '已發布' },
  { value: 'DRAFT', label: '草稿' },
  { value: 'RETIRED', label: '已下架' }
]

// 批次選擇相關計算屬性
const canShowBatchOperations = computed(() => {
  return selectedAnimals.value.length > 0 && (currentStatus.value === 'SUBMITTED' || currentStatus.value === 'PUBLISHED')
})

const isAllSelected = computed(() => {
  return animals.value.length > 0 && selectedAnimals.value.length === animals.value.length
})

// 批次選擇函數
const toggleAnimal = (animalId: number) => {
  const index = selectedAnimals.value.indexOf(animalId)
  if (index > -1) {
    selectedAnimals.value.splice(index, 1)
  } else {
    selectedAnimals.value.push(animalId)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedAnimals.value = []
  } else {
    selectedAnimals.value = animals.value.map(animal => animal.animal_id)
  }
}

const clearSelection = () => {
  selectedAnimals.value = []
}

const getAnimalName = (animalId: number): string => {
  const animal = animals.value.find(a => a.animal_id === animalId)
  return animal?.name || `動物 #${animalId}`
}

// 載入動物列表
async function loadAnimals() {
  isLoading.value = true
  try {
    const response = await getAnimals({
      status: currentStatus.value as any,
      page: pagination.value.page,
      per_page: pagination.value.per_page
    })
    
    animals.value = response.animals
    pagination.value = {
      page: response.page,
      per_page: response.per_page,
      pages: response.pages,
      total: response.total
    }
    
    // 清除不在當前頁的選擇
    const currentAnimalIds = animals.value.map(a => a.animal_id)
    selectedAnimals.value = selectedAnimals.value.filter(id => currentAnimalIds.includes(id))
  } catch (error: any) {
    console.error('Load animals error:', error)
    alert('載入失敗: ' + (error.response?.data?.message || error.message))
  } finally {
    isLoading.value = false
  }
}

// 載入統計資料
async function loadStats() {
  try {
    const statuses = ['DRAFT', 'SUBMITTED', 'PUBLISHED', 'RETIRED']
    const requests = statuses.map(status => 
      getAnimals({ status: status as any, per_page: 1 })
    )
    
    const results = await Promise.all(requests)
    stats.value = {
      draft: results[0].total,
      submitted: results[1].total,
      published: results[2].total,
      retired: results[3].total
    }
  } catch (error) {
    console.error('Load stats error:', error)
  }
}

// 核准發布動物
async function publishAnimal(animalId: number) {
  if (!confirm('確定要核准發布此動物嗎?')) return
  
  isProcessing.value = true
  try {
    await publishAnimalAPI(animalId)
    alert('動物已發布')
    await loadAnimals()
    await loadStats()
  } catch (error: any) {
    console.error('Publish error:', error)
    alert('發布失敗: ' + (error.response?.data?.message || error.message))
  } finally {
    isProcessing.value = false
  }
}

// 批次操作函數
async function batchOperation(operation: 'publish' | 'retire') {
  if (selectedAnimals.value.length === 0) {
    alert('請先選擇要操作的動物')
    return
  }

  const operationText = operation === 'publish' ? '批次核准發布' : '批次下架'
  const confirmText = `確定要${operationText} ${selectedAnimals.value.length} 隻動物嗎？`
  
  if (!confirm(confirmText)) {
    return
  }

  batchProcessing.value = true

  try {
    let successCount = 0
    let failedCount = 0
    const errors: string[] = []

    for (const animalId of selectedAnimals.value) {
      try {
        if (operation === 'publish') {
          await publishAnimalAPI(animalId)
        } else {
          await retireAnimalAPI(animalId)
        }
        successCount++
      } catch (error: any) {
        failedCount++
        const errorMsg = error.response?.data?.message || error.message || '未知錯誤'
        errors.push(`動物 ID ${animalId}: ${errorMsg}`)
        console.error(`${operationText}動物 ${animalId} 失敗:`, error)
      }
    }

    // 顯示結果
    let message = `${operationText}完成！\n成功: ${successCount} 隻\n失敗: ${failedCount} 隻`
    if (errors.length > 0) {
      message += `\n\n錯誤詳情:\n${errors.slice(0, 3).join('\n')}`
      if (errors.length > 3) {
        message += `\n... 還有 ${errors.length - 3} 個錯誤`
      }
    }
    alert(message)

    selectedAnimals.value = []
    
    // 重新載入數據
    await loadAnimals()
    await loadStats()

  } catch (error: any) {
    console.error(`${operationText}錯誤:`, error)
    alert(`${operationText}失敗: ${error.message}`)
  } finally {
    batchProcessing.value = false
  }
}

// 批次拒絕函數
function openBatchRejectModal() {
  if (selectedAnimals.value.length === 0) {
    alert('請先選擇要拒絕的動物')
    return
  }
  
  isBatchReject.value = true
  rejectingAnimalId.value = null
  rejectionReason.value = ''
  showRejectModal.value = true
}

// 不核准動物 - 開啟拒絕原因 Modal (問題4、問題5)
function openRejectModal(animalId: number) {
  isBatchReject.value = false
  rejectingAnimalId.value = animalId
  rejectionReason.value = ''
  showRejectModal.value = true
}

function closeRejectModal() {
  showRejectModal.value = false
  rejectingAnimalId.value = null
  rejectionReason.value = ''
  isBatchReject.value = false
}

async function confirmReject() {
  if (!rejectionReason.value.trim()) {
    alert('請輸入拒絕原因')
    return
  }
  
  if (isBatchReject.value) {
    // 批次拒絕
    if (selectedAnimals.value.length === 0) return
    
    batchProcessing.value = true
    try {
      let successCount = 0
      let failedCount = 0
      const errors: string[] = []

      for (const animalId of selectedAnimals.value) {
        try {
          await rejectAnimalAPI(animalId, rejectionReason.value.trim())
          successCount++
        } catch (error: any) {
          failedCount++
          const errorMsg = error.response?.data?.message || error.message || '未知錯誤'
          errors.push(`動物 ID ${animalId}: ${errorMsg}`)
          console.error(`批次拒絕動物 ${animalId} 失敗:`, error)
        }
      }

      // 顯示結果
      let message = `批次拒絕完成！\n成功: ${successCount} 隻\n失敗: ${failedCount} 隻`
      if (errors.length > 0) {
        message += `\n\n錯誤詳情:\n${errors.slice(0, 3).join('\n')}`
        if (errors.length > 3) {
          message += `\n... 還有 ${errors.length - 3} 個錯誤`
        }
      }
      alert(message)

      selectedAnimals.value = []
      closeRejectModal()
      await loadAnimals()
      await loadStats()

    } catch (error: any) {
      console.error('批次拒絕錯誤:', error)
      alert('批次拒絕失敗: ' + error.message)
    } finally {
      batchProcessing.value = false
    }
  } else {
    // 單個拒絕
    if (!rejectingAnimalId.value) return
    
    isProcessing.value = true
    try {
      await rejectAnimalAPI(rejectingAnimalId.value, rejectionReason.value.trim())
      alert('已拒絕批准,並已通知送養者')
      closeRejectModal()
      await loadAnimals()
      await loadStats()
    } catch (error: any) {
      console.error('Reject error:', error)
      alert('拒絕失敗: ' + (error.response?.data?.message || error.message))
    } finally {
      isProcessing.value = false
    }
  }
}

// 下架動物
async function retireAnimal(animalId: number) {
  if (!confirm('確定要下架此動物嗎?')) return
  
  isProcessing.value = true
  try {
    await retireAnimalAPI(animalId)
    alert('動物已下架')
    await loadAnimals()
    await loadStats()
  } catch (error: any) {
    console.error('Retire error:', error)
    alert('下架失敗: ' + (error.response?.data?.message || error.message))
  } finally {
    isProcessing.value = false
  }
}

// 查看詳情
function viewDetail(animalId: number) {
  router.push(`/animals/${animalId}`)
}

// 切換頁面
function changePage(page: number) {
  pagination.value.page = page
  loadAnimals()
}

// 工具函數
function getSpeciesText(species: string): string {
  const map: Record<string, string> = {
    CAT: '貓',
    DOG: '狗'
  }
  return map[species] || species
}

function getSexText(sex: string): string {
  const map: Record<string, string> = {
    MALE: '公',
    FEMALE: '母',
    UNKNOWN: '未知'
  }
  return map[sex] || sex
}

function getStatusText(status: string): string {
  const map: Record<string, string> = {
    DRAFT: '草稿',
    SUBMITTED: '待審核',
    PUBLISHED: '已發布',
    RETIRED: '已下架'
  }
  return map[status] || status
}

function getStatusClass(status: string): string {
  const map: Record<string, string> = {
    DRAFT: 'bg-gray-100 text-gray-800',
    SUBMITTED: 'bg-orange-100 text-orange-800',
    PUBLISHED: 'bg-green-100 text-green-800',
    RETIRED: 'bg-red-100 text-red-800'
  }
  return map[status] || 'bg-gray-100 text-gray-800'
}

function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatDateOnly(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-TW', { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit'
  })
}

function getCurrentStatusLabel(): string {
  const option = statusOptions.find(opt => opt.value === currentStatus.value)
  return option?.label || ''
}

onMounted(() => {
  loadAnimals()
  loadStats()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Modal 樣式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background-color: white;
  border-radius: 0.5rem;
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e5e7eb;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
}

.modal-close {
  padding: 0.5rem;
  background-color: transparent;
  border: none;
  cursor: pointer;
  color: #6b7280;
  transition: color 0.2s;
}

.modal-close:hover {
  color: #111827;
}

.modal-body {
  padding: 1.5rem;
}

.form-label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #374151;
}

.form-label.required::after {
  content: ' *';
  color: #ef4444;
}

.form-textarea {
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  transition: border-color 0.2s;
  resize: vertical;
}

.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.alert {
  padding: 1rem;
  border-radius: 0.375rem;
}

.alert-warning {
  background-color: #fef3c7;
  color: #92400e;
  border: 1px solid #fcd34d;
}

.form-actions {
  margin-top: 1.5rem;
}

.btn-secondary {
  padding: 0.625rem 1.5rem;
  background-color: white;
  color: #374151;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #f3f4f6;
}

.btn-reject {
  padding: 0.625rem 1.5rem;
  background-color: #dc2626;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-reject:hover:not(:disabled) {
  background-color: #b91c1c;
}

.btn-reject:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}
</style>

