<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 返回按鈕 -->
      <button
        @click="$router.back()"
        class="mb-6 flex items-center text-gray-600 hover:text-gray-900 transition"
      >
        <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        返回列表
      </button>

      <!-- 載入中 -->
      <div v-if="loading" class="flex justify-center py-12">
        <svg class="animate-spin h-12 w-12 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <!-- 錯誤訊息 -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
        <p class="text-red-800">{{ error }}</p>
      </div>

      <!-- 收容所詳情 -->
      <div v-else-if="shelter" class="space-y-6">
        <!-- 收容所資訊卡片 -->
        <div class="bg-white rounded-lg shadow-lg overflow-hidden">
          <div class="p-6">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <h1 class="text-3xl font-bold text-gray-900 mb-2">{{ shelter.name }}</h1>
                <span 
                  :class="[
                    shelter.verified 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-800'
                  ]"
                  class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                >
                  {{ shelter.verified ? '✓ 已驗證收容所' : '⏳ 未驗證' }}
                </span>
              </div>
              
              <!-- 編輯按鈕 (僅管理員) -->
              <button
                v-if="isAdmin"
                @click="editMode = !editMode"
                class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition"
              >
                {{ editMode ? '取消編輯' : '編輯資訊' }}
              </button>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
              <!-- 聯絡資訊 -->
              <div class="space-y-4">
                <h2 class="text-lg font-semibold text-gray-900 border-b pb-2">聯絡資訊</h2>
                
                <div class="flex items-start">
                  <svg class="h-5 w-5 text-gray-400 mr-3 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  <div>
                    <p class="text-sm text-gray-500">地址</p>
                    <p class="text-gray-900">{{ formatAddress(shelter.address) }}</p>
                  </div>
                </div>

                <div class="flex items-start">
                  <svg class="h-5 w-5 text-gray-400 mr-3 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  <div>
                    <p class="text-sm text-gray-500">Email</p>
                    <a :href="`mailto:${shelter.contact_email}`" class="text-indigo-600 hover:text-indigo-800">
                      {{ shelter.contact_email }}
                    </a>
                  </div>
                </div>

                <div class="flex items-start">
                  <svg class="h-5 w-5 text-gray-400 mr-3 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  <div>
                    <p class="text-sm text-gray-500">電話</p>
                    <a :href="`tel:${shelter.contact_phone}`" class="text-indigo-600 hover:text-indigo-800">
                      {{ shelter.contact_phone }}
                    </a>
                  </div>
                </div>

                <div v-if="shelter.website" class="flex items-start">
                  <svg class="h-5 w-5 text-gray-400 mr-3 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                  </svg>
                  <div>
                    <p class="text-sm text-gray-500">網站</p>
                    <a :href="shelter.website" target="_blank" class="text-indigo-600 hover:text-indigo-800">
                      {{ shelter.website }}
                    </a>
                  </div>
                </div>
              </div>

              <!-- 其他資訊 -->
              <div class="space-y-4">
                <h2 class="text-lg font-semibold text-gray-900 border-b pb-2">其他資訊</h2>
                
                <div v-if="shelter.description" class="flex items-start">
                  <svg class="h-5 w-5 text-gray-400 mr-3 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7" />
                  </svg>
                  <div>
                    <p class="text-sm text-gray-500">簡介</p>
                    <p class="text-gray-900">{{ shelter.description }}</p>
                  </div>
                </div>

                <div v-if="shelter.capacity" class="flex items-start">
                  <svg class="h-5 w-5 text-gray-400 mr-3 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                  </svg>
                  <div>
                    <p class="text-sm text-gray-500">容量</p>
                    <p class="text-gray-900">{{ shelter.capacity }} 隻動物</p>
                  </div>
                </div>

                <div class="flex items-start">
                  <svg class="h-5 w-5 text-gray-400 mr-3 mt-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <div>
                    <p class="text-sm text-gray-500">建立時間</p>
                    <p class="text-gray-900">{{ formatDate(shelter.created_at) }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Tab 導航 -->
        <div class="bg-white rounded-lg shadow overflow-hidden">
          <div class="border-b border-gray-200">
            <nav class="-mb-px flex">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                @click="currentTab = tab.id"
                :class="[
                  currentTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                  'flex-1 whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
                ]"
              >
                {{ tab.name }}
              </button>
            </nav>
          </div>

          <!-- Tab 內容 -->
          <div class="p-6">
            <!-- 動物列表 Tab -->
            <div v-if="currentTab === 'animals'" class="space-y-4">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-semibold">收容動物 ({{ animals.length }})</h3>
              </div>

              <div v-if="loadingAnimals" class="text-center py-8">
                <svg class="animate-spin h-8 w-8 text-indigo-600 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>

              <div v-else-if="animals.length === 0" class="text-center py-8 text-gray-500">
                目前沒有收容動物
              </div>

              <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div
                  v-for="animal in animals"
                  :key="animal.animal_id"
                  @click="$router.push(`/animals/${animal.animal_id}`)"
                  class="border rounded-lg p-4 hover:shadow-md transition cursor-pointer"
                >
                  <div class="flex items-start justify-between mb-2">
                    <h4 class="font-semibold text-gray-900">{{ animal.name }}</h4>
                    <span 
                      :class="getStatusColor(animal.adoption_status)"
                      class="px-2 py-1 rounded text-xs font-medium"
                    >
                      {{ getStatusText(animal.adoption_status) }}
                    </span>
                  </div>
                  <p class="text-sm text-gray-600">{{ animal.breed }}</p>
                  <p class="text-xs text-gray-500 mt-1">{{ animal.age }} 歲 · {{ animal.gender === 'MALE' ? '公' : '母' }}</p>
                </div>
              </div>
            </div>

            <!-- 聯絡表單 Tab -->
            <div v-else-if="currentTab === 'contact'" class="max-w-2xl">
              <h3 class="text-lg font-semibold mb-4">聯絡收容所</h3>
              <form @submit.prevent="handleContact" class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">姓名</label>
                  <input
                    v-model="contactForm.name"
                    type="text"
                    required
                    class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    v-model="contactForm.email"
                    type="email"
                    required
                    class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-1">訊息</label>
                  <textarea
                    v-model="contactForm.message"
                    rows="6"
                    required
                    class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  ></textarea>
                </div>
                
                <button
                  type="submit"
                  :disabled="submitting"
                  class="w-full py-2 px-4 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:bg-gray-400 transition"
                >
                  {{ submitting ? '發送中...' : '發送訊息' }}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { getShelter } from '@/api/shelters'
import { getAnimals } from '@/api/animals'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const shelter = ref<any>(null)
const animals = ref<any[]>([])
const loading = ref(false)
const loadingAnimals = ref(false)
const error = ref('')
const editMode = ref(false)
const currentTab = ref('animals')
const submitting = ref(false)

const contactForm = ref({
  name: '',
  email: '',
  message: ''
})

const tabs = [
  { id: 'animals', name: '收容動物' },
  { id: 'contact', name: '聯絡我們' }
]

const isAdmin = computed(() => authStore.user?.role === 'ADMIN')

onMounted(async () => {
  await fetchShelter()
  await fetchAnimals()
})

async function fetchShelter() {
  loading.value = true
  error.value = ''
  
  try {
    const shelterId = parseInt(route.params.id as string)
    shelter.value = await getShelter(shelterId)
  } catch (err: any) {
    error.value = err.response?.data?.message || '載入收容所資訊失敗'
  } finally {
    loading.value = false
  }
}

async function fetchAnimals() {
  loadingAnimals.value = true
  
  try {
    const shelterId = parseInt(route.params.id as string)
    const response = await getAnimals({ shelter_id: shelterId, per_page: 100 })
    animals.value = response.animals
  } catch (err) {
    console.error('載入動物列表失敗:', err)
  } finally {
    loadingAnimals.value = false
  }
}

function formatAddress(address: any) {
  if (typeof address === 'string') {
    return address
  }
  if (address && typeof address === 'object') {
    return `${address.city || ''}${address.district || ''}${address.street || ''}`
  }
  return '地址未提供'
}

function formatDate(dateString: string) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('zh-TW')
}

function getStatusColor(status: string) {
  const colors: Record<string, string> = {
    AVAILABLE: 'bg-green-100 text-green-800',
    PENDING: 'bg-yellow-100 text-yellow-800',
    ADOPTED: 'bg-blue-100 text-blue-800',
    UNAVAILABLE: 'bg-gray-100 text-gray-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

function getStatusText(status: string) {
  const text: Record<string, string> = {
    AVAILABLE: '可領養',
    PENDING: '審核中',
    ADOPTED: '已領養',
    UNAVAILABLE: '不可領養'
  }
  return text[status] || status
}

async function handleContact() {
  submitting.value = true
  
  try {
    // TODO: 實作聯絡 API
    await new Promise(resolve => setTimeout(resolve, 1000))
    alert('訊息已發送!')
    contactForm.value = { name: '', email: '', message: '' }
  } catch (err) {
    alert('發送失敗,請稍後再試')
  } finally {
    submitting.value = false
  }
}
</script>