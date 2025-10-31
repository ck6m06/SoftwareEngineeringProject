<template>
  <router-link
    :to="`/animals/${animal.animal_id}`"
    class="animal-card block bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden"
  >
    <!-- 圖片 -->
    <div class="relative h-48 bg-gray-200">
      <img
        v-if="primaryImage"
        :src="primaryImage"
        :alt="animal.name || '未命名動物'"
        class="w-full h-full object-cover"
      />
      <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
        <span class="text-4xl">🐾</span>
      </div>

      <!-- 狀態標籤 -->
      <div class="absolute top-2 right-2">
        <span
          class="px-2 py-1 text-xs font-semibold rounded-full"
          :class="statusClass"
        >
          {{ statusText }}
        </span>
      </div>

      <!-- 申請審核中標籤 -->
      <div v-if="animal.has_pending_application && animal.status === 'PUBLISHED'" class="absolute bottom-2 right-2">
        <span class="px-2 py-1 text-xs font-semibold rounded-full bg-orange-500 text-white">
          📝 領養申請審核中
        </span>
      </div>

      <!-- 我的寵物標籤 -->
      <div v-if="isMyAnimal" class="absolute top-2 left-2">
        <span class="px-2 py-1 text-xs font-semibold rounded-full bg-purple-500 text-white">
          👤 我的
        </span>
      </div>

      <!-- Featured 標籤 -->
      <div v-else-if="animal.featured" class="absolute top-2 left-2">
        <span class="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-400 text-yellow-900">
          ⭐ 精選
        </span>
      </div>
    </div>

    <!-- 內容 -->
    <div class="p-4">
      <!-- 名稱 -->
      <h3 class="text-lg font-bold text-gray-900 mb-2 truncate">
        {{ animal.name || '未命名動物' }}
      </h3>

      <!-- 基本資訊 -->
      <div class="space-y-1 text-sm text-gray-600 mb-3">
        <div class="flex items-center">
          <span class="mr-2">物種：</span>
          <span>{{ speciesText }} </span>
        </div>
        <div class="flex items-center">
          <span class="mr-2">品種：</span>
          <span>{{ animal.breed }}</span>
        </div>
        <div class="flex items-center" v-if="animal.sex">
          <span class="mr-2">性別：</span>
          <span>{{ sexText }}</span>
        </div>
        <div class="flex items-center" v-if="animal.color">
          <span class="mr-2">顏色：</span>
          <span>{{ animal.color }}</span>
        </div>
        <div class="flex items-center" v-if="age">
          <span class="mr-2">年齡：</span>
          <span>{{ age }}</span>
        </div>
      </div>

      <!-- 描述 (截斷) -->
      <p v-if="animal.description" class="text-sm text-gray-500 line-clamp-2 mb-3">
        {{ animal.description }}
      </p>

      <!-- Footer -->
      <div class="flex items-center justify-between text-xs text-gray-400 pt-3 border-t border-gray-100">
        <span v-if="animal.shelter_id">
          🏠 收容所
        </span>
        <span v-else-if="animal.owner_id">
          👤 個人送養
        </span>
        <span>
          {{ formattedDate }}
        </span>
      </div>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

interface Animal {
  animal_id: number
  name?: string
  species?: 'CAT' | 'DOG'
  breed?: string
  color?: string
  sex?: 'MALE' | 'FEMALE' | 'UNKNOWN'
  dob?: string
  description?: string
  status: 'DRAFT' | 'SUBMITTED' | 'PUBLISHED' | 'ADOPTED' | 'RETIRED'
  shelter_id?: number
  owner_id?: number
  created_by?: number
  featured?: boolean
  images?: Array<{ url: string; order: number }>
  created_at: string
  has_pending_application?: boolean
}

const props = defineProps<{
  animal: Animal
}>()

// 是否為我的動物
const isMyAnimal = computed(() => {
  if (!authStore.user) return false
  return props.animal.created_by === authStore.user.user_id
})
// 主要圖片
const primaryImage = computed(() => {
  if (props.animal.images && props.animal.images.length > 0) {
    const sorted = [...props.animal.images].sort((a, b) => a.order - b.order)
    return sorted[0].url
  }
  return null
})

// 物種文字
const speciesText = computed(() => {
  const map: Record<string, string> = {
    CAT: '貓',
    DOG: '狗',
  }
  return props.animal.species ? map[props.animal.species] : '未知'
})

// 性別文字
const sexText = computed(() => {
  const map: Record<string, string> = {
    MALE: '公',
    FEMALE: '母',
    UNKNOWN: '未知',
  }
  return props.animal.sex ? map[props.animal.sex] : '未知'
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
  return map[props.animal.status] || '未知'
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
  return map[props.animal.status] || 'bg-gray-100 text-gray-800'
})

// 計算年齡
const age = computed(() => {
  if (!props.animal.dob) return null

  const birthDate = new Date(props.animal.dob)
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
  const date = new Date(props.animal.created_at)
  return date.toLocaleDateString('zh-TW', { year: 'numeric', month: '2-digit', day: '2-digit' })
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
