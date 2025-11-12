<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 頁面標題 -->
      <div class="mb-6">
        <h1 class="text-3xl font-bold text-gray-900">📋 審計日誌</h1>
        <p class="mt-2 text-gray-600">系統操作記錄與審計追蹤</p>
      </div>

      <!-- 篩選區域 -->
      <div class="bg-white rounded-lg shadow p-6 mb-6">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <!-- 動作類型篩選 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">動作類型</label>
            <input
              v-model="filters.action"
              type="text"
              placeholder="例: login, approve"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <!-- 資源類型篩選 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">資源類型</label>
            <select
              v-model="filters.target_type"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">全部</option>
              <option value="user">使用者</option>
              <option value="animal">動物</option>
              <option value="application">申請</option>
              <option value="shelter">收容所</option>
              <option value="medical_record">醫療記錄</option>
            </select>
          </div>

          <!-- 開始時間 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">開始時間</label>
            <input
              v-model="filters.start_time"
              type="datetime-local"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <!-- 結束時間 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">結束時間</label>
            <input
              v-model="filters.end_time"
              type="datetime-local"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <!-- 篩選按鈕 -->
        <div class="mt-4 flex gap-2">
          <button
            @click="applyFilters"
            class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition"
          >
            🔍 搜尋
          </button>
          <button
            @click="resetFilters"
            class="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition"
          >
            🔄 重置
          </button>
        </div>
      </div>

      <!-- 載入狀態 -->
      <div v-if="loading" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        <p class="mt-4 text-gray-600">載入中...</p>
      </div>

      <!-- 錯誤訊息 -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-lg p-4">
        <p class="text-red-800">❌ {{ error }}</p>
      </div>

      <!-- 審計日誌列表 -->
      <div v-else-if="logs.length > 0" class="bg-white rounded-lg shadow overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  時間
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  執行者
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  動作
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  目標
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  詳情
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="log in logs"
                :key="log.audit_log_id"
                class="hover:bg-gray-50 transition"
              >
                <!-- 時間 -->
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatDateTime(log.timestamp) }}
                </td>

                <!-- 執行者 -->
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <span v-if="log.actor_email" class="text-blue-600">
                    {{ log.actor_email }}
                  </span>
                  <span v-else class="text-gray-400 italic">系統</span>
                </td>

                <!-- 動作 -->
                <td class="px-6 py-4 whitespace-nowrap">
                  <span
                    :class="getActionColor(log.action)"
                    class="px-2 py-1 text-xs font-medium rounded-full"
                  >
                    {{ log.action }}
                  </span>
                </td>

                <!-- 目標 -->
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <span v-if="log.target_type">
                    {{ log.target_type }}
                    <span v-if="log.target_id" class="text-gray-500">#{{ log.target_id }}</span>
                  </span>
                  <span v-else class="text-gray-400">-</span>
                </td>

                <!-- 詳情按鈕 -->
                <td class="px-6 py-4 whitespace-nowrap text-sm">
                  <button
                    @click="toggleDetails(log.audit_log_id)"
                    class="text-blue-600 hover:text-blue-800 font-medium"
                  >
                    {{ expandedLogId === log.audit_log_id ? '▼ 收起' : '▶ 展開' }}
                  </button>
                </td>
              </tr>

              <!-- 展開的詳情 -->
              <tr v-if="expandedLogId" :key="`detail-${expandedLogId}`">
                <td colspan="5" class="px-6 py-4 bg-gray-50">
                  <div v-if="getExpandedLog()" class="space-y-4">
                    <!-- 備註 -->
                    <div v-if="getExpandedLog()!.notes">
                      <h4 class="font-semibold text-gray-700 mb-1">📝 備註</h4>
                      <p class="text-sm text-gray-600">{{ getExpandedLog()!.notes }}</p>
                    </div>

                    <!-- 變更前狀態 -->
                    <div v-if="getExpandedLog()!.before_state">
                      <h4 class="font-semibold text-gray-700 mb-1">🔴 變更前</h4>
                      <pre class="text-xs bg-white p-3 rounded border border-gray-200 overflow-auto">{{ JSON.stringify(getExpandedLog()!.before_state, null, 2) }}</pre>
                    </div>

                    <!-- 變更後狀態 -->
                    <div v-if="getExpandedLog()!.after_state">
                      <h4 class="font-semibold text-gray-700 mb-1">🟢 變更後</h4>
                      <pre class="text-xs bg-white p-3 rounded border border-gray-200 overflow-auto">{{ JSON.stringify(getExpandedLog()!.after_state, null, 2) }}</pre>
                    </div>

                    <!-- 收容所關聯 -->
                    <div v-if="getExpandedLog()!.shelter_id">
                      <h4 class="font-semibold text-gray-700 mb-1">🏠 關聯收容所</h4>
                      <p class="text-sm text-gray-600">Shelter ID: {{ getExpandedLog()!.shelter_id }}</p>
                    </div>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分頁控制 -->
        <div v-if="pagination.pages > 1" class="px-6 py-4 bg-gray-50 border-t border-gray-200">
          <div class="flex items-center justify-between">
            <div class="text-sm text-gray-700">
              第 {{ pagination.page }} 頁，共 {{ pagination.pages }} 頁
              (總計 {{ pagination.total }} 筆記錄)
            </div>
            <div class="flex gap-2">
              <button
                @click="goToPage(pagination.page - 1)"
                :disabled="pagination.page === 1"
                class="px-3 py-1 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
              >
                上一頁
              </button>
              <button
                @click="goToPage(pagination.page + 1)"
                :disabled="pagination.page === pagination.pages"
                class="px-3 py-1 border border-gray-300 rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
              >
                下一頁
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 空狀態 -->
      <div v-else class="bg-white rounded-lg shadow p-12 text-center">
        <p class="text-gray-500 text-lg">📭 目前沒有審計日誌</p>
        <p class="text-gray-400 text-sm mt-2">系統操作會自動記錄在此</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getAuditLogs, type AuditLog, type AuditLogFilters } from '../api/auditLogs'

// 狀態
const logs = ref<AuditLog[]>([])
const loading = ref(false)
const error = ref('')
const expandedLogId = ref<number | null>(null)

// 篩選條件
const filters = ref<AuditLogFilters>({
  action: '',
  target_type: '',
  start_time: '',
  end_time: '',
  page: 1,
  per_page: 20
})

// 分頁資訊
const pagination = ref({
  page: 1,
  per_page: 20,
  total: 0,
  pages: 1
})

// 載入審計日誌
const loadLogs = async () => {
  loading.value = true
  error.value = ''
  
  try {
    // 轉換時間格式為 ISO 8601
    const queryFilters: AuditLogFilters = {
      ...filters.value,
      start_time: filters.value.start_time 
        ? new Date(filters.value.start_time).toISOString() 
        : undefined,
      end_time: filters.value.end_time 
        ? new Date(filters.value.end_time).toISOString() 
        : undefined
    }
    
    // 移除空值
    Object.keys(queryFilters).forEach(key => {
      const value = queryFilters[key as keyof AuditLogFilters]
      if (value === '' || value === undefined) {
        delete queryFilters[key as keyof AuditLogFilters]
      }
    })
    
    const response = await getAuditLogs(queryFilters)
    logs.value = response.audit_logs || []
    pagination.value = response.pagination || {
      page: 1,
      per_page: 20,
      total: 0,
      pages: 1
    }
    console.log('✅ 審計日誌載入成功:', logs.value.length, '筆')
    console.log('分頁資訊:', pagination.value)
  } catch (err: any) {
    console.error('❌ 載入審計日誌失敗:', err)
    console.error('錯誤詳情:', err.response?.data)
    error.value = err.response?.data?.message || err.message || '無法載入審計日誌'
  } finally {
    loading.value = false
  }
}

// 套用篩選
const applyFilters = () => {
  filters.value.page = 1
  loadLogs()
}

// 重置篩選
const resetFilters = () => {
  filters.value = {
    action: '',
    target_type: '',
    start_time: '',
    end_time: '',
    page: 1,
    per_page: 20
  }
  loadLogs()
}

// 切換詳情展開
const toggleDetails = (logId: number) => {
  expandedLogId.value = expandedLogId.value === logId ? null : logId
}

// 取得展開的日誌
const getExpandedLog = () => {
  if (!expandedLogId.value) return null
  return logs.value.find(log => log.audit_log_id === expandedLogId.value)
}

// 切換頁碼
const goToPage = (page: number) => {
  filters.value.page = page
  loadLogs()
}

// 格式化時間
const formatDateTime = (timestamp: string) => {
  return new Date(timestamp).toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 取得動作顏色
const getActionColor = (action: string) => {
  if (action.includes('login')) return 'bg-blue-100 text-blue-800'
  if (action.includes('create')) return 'bg-green-100 text-green-800'
  if (action.includes('update') || action.includes('approve')) return 'bg-yellow-100 text-yellow-800'
  if (action.includes('delete') || action.includes('reject')) return 'bg-red-100 text-red-800'
  if (action.includes('verify')) return 'bg-purple-100 text-purple-800'
  return 'bg-gray-100 text-gray-800'
}

// 初始化
onMounted(() => {
  loadLogs()
})
</script>
