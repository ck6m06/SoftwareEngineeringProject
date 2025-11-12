<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 標題與搜尋列 -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">收容所列表</h1>
        
        <!-- 搜尋與篩選 -->
        <div class="bg-white rounded-lg shadow p-4 grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">城市</label>
            <select 
              v-model="filters.city"
              @change="handleFilterChange"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option value="">全部城市</option>
              <option value="台北市">台北市</option>
              <option value="新北市">新北市</option>
              <option value="桃園市">桃園市</option>
              <option value="台中市">台中市</option>
              <option value="台南市">台南市</option>
              <option value="高雄市">高雄市</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">驗證狀態</label>
            <select 
              v-model="verifiedFilter"
              @change="handleFilterChange"
              class="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option value="">全部</option>
              <option value="true">已驗證</option>
              <option value="false">未驗證</option>
            </select>
          </div>
          
          <div class="md:col-span-2 flex items-end">
            <button
              @click="resetFilters"
              class="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
            >
              清除篩選
            </button>
          </div>
        </div>
      </div>

      <!-- 載入中 -->
      <div v-if="loading" class="flex justify-center py-12">
        <svg class="animate-spin h-12 w-12 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <!-- 錯誤訊息 -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <p class="text-red-800">{{ error }}</p>
      </div>

      <!-- 收容所列表 -->
      <div v-else-if="shelters.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="shelter in shelters"
          :key="shelter.shelter_id"
          @click="goToDetail(shelter.shelter_id)"
          class="bg-white rounded-lg shadow hover:shadow-lg transition cursor-pointer overflow-hidden"
        >
          <!-- 收容所卡片 -->
          <div class="p-6">
            <div class="flex items-start justify-between mb-4">
              <div class="flex-1">
                <h3 class="text-lg font-bold text-gray-900 mb-1">{{ shelter.name }}</h3>
                <span 
                  :class="[
                    shelter.verified 
                      ? "bg-green-100 text-green-800" 
                      : "bg-gray-100 text-gray-800"
                  ]"
                  class="inline-flex items-center px-2 py-1 rounded text-xs font-medium"
                >
                  {{ shelter.verified ? "✓ 已驗證" : "⏳ 未驗證" }}
                </span>
              </div>
            </div>

            <div class="space-y-2 text-sm text-gray-600">
              <div class="flex items-start">
                <svg class="h-5 w-5 text-gray-400 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <span>{{ formatAddress(shelter.address) }}</span>
              </div>

              <div class="flex items-center">
                <svg class="h-5 w-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <span>{{ shelter.contact_email }}</span>
              </div>

              <div class="flex items-center">
                <svg class="h-5 w-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                <span>{{ shelter.contact_phone }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 空狀態 -->
      <div v-else class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">找不到收容所</h3>
        <p class="mt-1 text-sm text-gray-500">請嘗試調整搜尋條件</p>
      </div>

      <!-- 分頁 -->
      <div v-if="totalPages > 1" class="mt-8 flex justify-center">
        <nav class="flex items-center space-x-2">
          <button
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="px-3 py-2 rounded-md bg-white border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            上一頁
          </button>
          
          <span class="px-4 py-2 text-sm text-gray-700">
            第 {{ currentPage }} / {{ totalPages }} 頁
          </span>
          
          <button
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="px-3 py-2 rounded-md bg-white border border-gray-300 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一頁
          </button>
        </nav>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue"
import { useRouter } from "vue-router"
import { getShelters, type ShelterFilters } from "@/api/shelters"

const router = useRouter()

const shelters = ref<any[]>([])
const loading = ref(false)
const error = ref("")
const total = ref(0)
const currentPage = ref(1)
const perPage = ref(12)

const filters = ref<ShelterFilters>({
  city: "",
  page: 1,
  per_page: 12
})

const verifiedFilter = ref("")

const totalPages = computed(() => Math.ceil(total.value / perPage.value))

onMounted(() => {
  fetchShelters()
})

async function fetchShelters() {
  loading.value = true
  error.value = ""
  
  try {
    const params: ShelterFilters = {
      ...filters.value,
      page: currentPage.value,
      per_page: perPage.value
    }
    
    if (verifiedFilter.value !== "") {
      params.verified = verifiedFilter.value === "true"
    }
    
    const response = await getShelters(params)
    shelters.value = response.shelters
    total.value = response.total
  } catch (err: any) {
    error.value = err.response?.data?.message || "載入收容所列表失敗"
  } finally {
    loading.value = false
  }
}

function handleFilterChange() {
  currentPage.value = 1
  fetchShelters()
}

function resetFilters() {
  filters.value = {
    city: "",
    page: 1,
    per_page: 12
  }
  verifiedFilter.value = ""
  currentPage.value = 1
  fetchShelters()
}

function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    fetchShelters()
  }
}

function goToDetail(shelterId: number) {
  router.push(`/shelters/${shelterId}`)
}

function formatAddress(address: any) {
  if (typeof address === "string") {
    return address
  }
  if (address && typeof address === "object") {
    return `${address.city || ""}${address.district || ""}${address.street || ""}`
  }
  return "地址未提供"
}
</script>
