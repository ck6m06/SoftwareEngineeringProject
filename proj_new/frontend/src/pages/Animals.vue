<template>
  <div class="animals-page min-h-screen bg-gray-50 py-8">
    <div class="container mx-auto px-4 max-w-7xl">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-4xl font-bold text-gray-900 mb-2">尋找您的毛小孩</h1>
        <p class="text-gray-600">每一隻動物都值得一個溫暖的家 ❤️</p>
      </div>

      <!-- 搜尋與篩選區域 -->
      <div class="bg-white p-6 rounded-lg shadow-md mb-8">
        <!-- 第一排 - 基本篩選 -->
        <div class="grid md:grid-cols-4 gap-4">
          <!-- 搜尋關鍵字 -->
          <div class="md:col-span-2">
            <label class="block text-sm font-medium text-gray-700 mb-2">搜尋</label>
            <input
              v-model="filters.q"
              type="text"
              placeholder="搜尋動物名稱、品種..."
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              @keyup.enter="handleSearch"
            />
          </div>

          <!-- 物種篩選 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">物種</label>
            <select
              v-model="filters.species"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="handleSearch"
            >
              <option value="">全部</option>
              <option value="CAT">貓</option>
              <option value="DOG">狗</option>
            </select>
          </div>

          <!-- 性別篩選 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">性別</label>
            <select
              v-model="filters.sex"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="handleSearch"
            >
              <option value="">全部</option>
              <option value="MALE">公</option>
              <option value="FEMALE">母</option>
            </select>
          </div>
        </div>

        <!-- 第二排 - 進階篩選 -->
        <div class="grid md:grid-cols-4 gap-4 mt-4">
          <!-- 年齡篩選 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">年齡</label>
            <select
              v-model="ageRange"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="handleAgeChange"
            >
              <option value="">全部年齡</option>
              <option value="0-6">幼年 (0-6個月)</option>
              <option value="6-12">青少年 (6個月-1歲)</option>
              <option value="12-36">成年 (1-3歲)</option>
              <option value="36-84">中年 (3-7歲)</option>
              <option value="84-999">老年 (7歲以上)</option>
            </select>
          </div>

          <!-- 地區篩選 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">地區</label>
            <select
              v-model="filters.region"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="handleSearch"
            >
              <option value="">全部地區</option>
              <option value="台北市">台北市</option>
              <option value="新北市">新北市</option>
              <option value="桃園市">桃園市</option>
              <option value="台中市">台中市</option>
              <option value="台南市">台南市</option>
              <option value="高雄市">高雄市</option>
              <option value="新竹市">新竹市</option>
              <option value="新竹縣">新竹縣</option>
              <option value="苗栗縣">苗栗縣</option>
              <option value="彰化縣">彰化縣</option>
              <option value="南投縣">南投縣</option>
              <option value="雲林縣">雲林縣</option>
              <option value="嘉義市">嘉義市</option>
              <option value="嘉義縣">嘉義縣</option>
              <option value="屏東縣">屏東縣</option>
              <option value="宜蘭縣">宜蘭縣</option>
              <option value="花蓮縣">花蓮縣</option>
              <option value="台東縣">台東縣</option>
              <option value="澎湖縣">澎湖縣</option>
              <option value="金門縣">金門縣</option>
              <option value="連江縣">連江縣</option>
            </select>
          </div>

          <!-- 來源篩選 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">來源</label>
            <select
              v-model="filters.source_type"
              class="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              @change="handleSearch"
            >
              <option value="">全部來源</option>
              <option value="shelter">收容所</option>
              <option value="personal">個人送養</option>
            </select>
          </div>
        </div>

        <!-- 搜尋按鈕 -->
        <div class="mt-4 flex justify-end">
          <button
            @click="handleReset"
            class="mr-2 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
          >
            清除篩選
          </button>
          <button
            @click="handleSearch"
            class="px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
          >
            搜尋
          </button>
        </div>
      </div>

      <!-- Loading 狀態 -->
      <div v-if="isLoading && !animals.length" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-600">載入中...</p>
      </div>

      <!-- 錯誤訊息 -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
        載入失敗: {{ error }}
      </div>

      <!-- 動物列表 -->
      <div v-else-if="animals.length > 0">
        <!-- 結果摘要 -->
        <div class="mb-4 text-sm text-gray-600">
          找到 {{ pagination.total }} 隻動物，顯示第 {{ pagination.page }} 頁 (共 {{ pagination.pages }} 頁)
        </div>

        <!-- 卡片網格 -->
        <div class="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8">
          <AnimalCard
            v-for="animal in animals"
            :key="animal.animal_id"
            :animal="animal"
          />
        </div>

        <!-- 分頁 -->
        <div class="flex justify-center items-center space-x-2">
          <button
            @click="goToPage(pagination.page - 1)"
            :disabled="pagination.page === 1"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            上一頁
          </button>

          <span class="text-sm text-gray-600">
            第 {{ pagination.page }} / {{ pagination.pages }} 頁
          </span>

          <button
            @click="goToPage(pagination.page + 1)"
            :disabled="pagination.page >= pagination.pages"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一頁
          </button>
        </div>
      </div>

      <!-- 無結果 -->
      <div v-else class="text-center py-12">
        <span class="text-6xl mb-4 block">🐾</span>
        <p class="text-xl text-gray-600">找不到符合條件的動物</p>
        <p class="text-sm text-gray-500 mt-2">試試調整搜尋條件</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { getAnimals, type Animal, type AnimalFilters } from '@/api/animals'
import AnimalCard from '@/components/animals/AnimalCard.vue'

const animals = ref<Animal[]>([])
const isLoading = ref(false)
const error = ref('')
const ageRange = ref('')

const filters = reactive<AnimalFilters>({
  q: '',
  species: undefined,
  sex: undefined,
  region: undefined,
  source_type: undefined,
  min_age: undefined,
  max_age: undefined,
  status: 'PUBLISHED',  // 只顯示已發布的
  page: 1,
  per_page: 12,
})

const pagination = reactive({
  page: 1,
  per_page: 12,
  total: 0,
  pages: 1,
})

// 載入動物列表
async function loadAnimals() {
  isLoading.value = true
  error.value = ''

  try {
    const response = await getAnimals(filters)
    animals.value = response.animals
    // API 回傳的分頁資訊在頂層,不是在 pagination 物件中
    pagination.page = response.page
    pagination.per_page = response.per_page
    pagination.total = response.total
    pagination.pages = response.pages
  } catch (err: any) {
    console.error('Load animals error:', err)
    error.value = err.response?.data?.message || '載入失敗'
  } finally {
    isLoading.value = false
  }
}

// 處理搜尋
function handleSearch() {
  filters.page = 1  // 重置到第一頁
  loadAnimals()
}

// 處理年齡範圍變更
function handleAgeChange() {
  if (ageRange.value === '') {
    filters.min_age = undefined
    filters.max_age = undefined
  } else {
    const [min, max] = ageRange.value.split('-').map(Number)
    filters.min_age = min
    filters.max_age = max === 999 ? undefined : max  // 999 表示無上限
  }
  handleSearch()
}

// 清除篩選
function handleReset() {
  filters.q = ''
  filters.species = undefined
  filters.sex = undefined
  filters.region = undefined
  filters.source_type = undefined
  filters.min_age = undefined
  filters.max_age = undefined
  ageRange.value = ''
  filters.page = 1
  loadAnimals()
}

// 切換頁面
function goToPage(page: number) {
  if (page < 1 || page > pagination.pages) return
  filters.page = page
  loadAnimals()
  // 滾動到頂部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 初始載入
onMounted(() => {
  loadAnimals()
})
</script>
