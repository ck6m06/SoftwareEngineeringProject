<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 標題列 -->
      <div class="mb-6 flex items-center justify-between">
        <h1 class="text-3xl font-bold text-gray-900">通知中心</h1>
        <button
          v-if="unreadCount > 0"
          @click="handleMarkAllAsRead"
          class="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition"
        >
          全部標為已讀
        </button>
      </div>

      <!-- 統計卡片 -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-8 w-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">全部通知</p>
              <p class="text-2xl font-semibold text-gray-900">{{ notifications.length }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-8 w-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">未讀通知</p>
              <p class="text-2xl font-semibold text-gray-900">{{ unreadCount }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white rounded-lg shadow p-6">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-4">
              <p class="text-sm font-medium text-gray-500">已讀通知</p>
              <p class="text-2xl font-semibold text-gray-900">{{ readNotifications.length }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 篩選標籤 -->
      <div class="bg-white rounded-lg shadow mb-6">
        <div class="border-b border-gray-200">
          <nav class="flex -mb-px">
            <button
              @click="currentFilter = 'all'"
              :class="[
                'px-6 py-4 text-sm font-medium border-b-2 transition',
                currentFilter === 'all'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              全部 ({{ notifications.length }})
            </button>
            <button
              @click="currentFilter = 'unread'"
              :class="[
                'px-6 py-4 text-sm font-medium border-b-2 transition',
                currentFilter === 'unread'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              未讀 ({{ unreadCount }})
            </button>
            <button
              @click="currentFilter = 'read'"
              :class="[
                'px-6 py-4 text-sm font-medium border-b-2 transition',
                currentFilter === 'read'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              已讀 ({{ readNotifications.length }})
            </button>
          </nav>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="bg-white rounded-lg shadow p-8 text-center">
        <svg class="animate-spin h-8 w-8 mx-auto text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="mt-4 text-gray-500">載入中...</p>
      </div>

      <!-- 空狀態 -->
      <div v-else-if="filteredNotifications.length === 0" class="bg-white rounded-lg shadow p-12 text-center">
        <svg class="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        <h3 class="text-lg font-medium text-gray-900 mb-2">目前沒有通知</h3>
        <p class="text-gray-500">
          {{ currentFilter === 'unread' ? '所有通知都已讀取' : '您目前沒有任何通知' }}
        </p>
      </div>

      <!-- 通知列表 -->
      <div v-else class="space-y-4">
        <div
          v-for="notification in filteredNotifications"
          :key="notification.notification_id"
          :class="[
            'bg-white rounded-lg shadow hover:shadow-md transition cursor-pointer',
            !notification.read && 'border-l-4 border-indigo-600'
          ]"
          @click="handleNotificationClick(notification)"
        >
          <div class="p-6">
            <div class="flex items-start justify-between">
              <div class="flex items-start space-x-4 flex-1">
                <!-- 圖示 -->
                <div class="flex-shrink-0">
                  <div
                    :class="[
                      'h-12 w-12 rounded-full flex items-center justify-center',
                      getNotificationColor(notification.type)
                    ]"
                  >
                    <svg
                      v-html="getNotificationIcon(notification.type)"
                      class="h-6 w-6 text-white"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                    ></svg>
                  </div>
                </div>

                <!-- 內容 -->
                <div class="flex-1 min-w-0">
                  <div class="flex items-center space-x-2 mb-1">
                    <p
                      :class="[
                        'text-sm font-medium',
                        !notification.read ? 'text-gray-900' : 'text-gray-600'
                      ]"
                    >
                      {{ getNotificationTitle(notification.type) }}
                    </p>
                    <span
                      v-if="!notification.read"
                      class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800"
                    >
                      未讀
                    </span>
                  </div>
                  <p class="text-sm text-gray-700 mb-2">
                    {{ getNotificationMessage(notification) }}
                  </p>
                  <p class="text-xs text-gray-500">
                    {{ formatDate(notification.created_at) }}
                  </p>
                </div>
              </div>

              <!-- 操作按鈕 -->
              <div class="flex items-center space-x-2 ml-4">
                <button
                  v-if="!notification.read"
                  @click.stop="handleMarkAsRead(notification.notification_id)"
                  class="p-2 text-indigo-600 hover:bg-indigo-50 rounded-full transition"
                  title="標為已讀"
                >
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </button>
                <button
                  @click.stop="handleDelete(notification.notification_id)"
                  class="p-2 text-red-600 hover:bg-red-50 rounded-full transition"
                  title="刪除"
                >
                  <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 分頁 (預留) -->
      <div v-if="filteredNotifications.length > 0" class="mt-8 flex justify-center">
        <p class="text-sm text-gray-500">
          顯示 {{ filteredNotifications.length }} 個通知
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useNotifications } from '@/composables/useNotifications'
import { formatDistanceToNow } from 'date-fns'
import { zhTW } from 'date-fns/locale'

type FilterType = 'all' | 'unread' | 'read'

const currentFilter = ref<FilterType>('all')

const {
  notifications,
  unreadCount,
  unreadNotifications,
  readNotifications,
  loading,
  fetchNotifications,
  markAsRead,
  markAllAsRead,
  deleteNotification,
  startPolling,
  stopPolling,
  getNotificationMessage,
} = useNotifications()

// 過濾的通知列表
const filteredNotifications = computed(() => {
  switch (currentFilter.value) {
    case 'unread':
      return unreadNotifications.value
    case 'read':
      return readNotifications.value
    default:
      return notifications.value
  }
})

// 標記單個通知為已讀
const handleMarkAsRead = async (notificationId: number) => {
  try {
    await markAsRead(notificationId)
  } catch (error) {
    console.error('Failed to mark as read:', error)
  }
}

// 標記全部為已讀
const handleMarkAllAsRead = async () => {
  try {
    await markAllAsRead()
  } catch (error) {
    console.error('Failed to mark all as read:', error)
  }
}

// 刪除通知
const handleDelete = async (notificationId: number) => {
  try {
    await deleteNotification(notificationId)
  } catch (error) {
    console.error('Failed to delete notification:', error)
  }
}

// 點擊通知
const handleNotificationClick = async (notification: any) => {
  if (!notification.read) {
    await handleMarkAsRead(notification.notification_id)
  }
  // TODO: 根據通知類型導航到相應頁面
}

// 格式化日期
const formatDate = (dateString: string) => {
  try {
    return formatDistanceToNow(new Date(dateString), {
      addSuffix: true,
      locale: zhTW,
    })
  } catch {
    return dateString
  }
}

// 獲取通知標題
const getNotificationTitle = (type: string): string => {
  const titleMap: Record<string, string> = {
    application_submitted: '領養申請已提交',
    application_approved: '領養申請已通過',
    application_rejected: '領養申請未通過',
    application_under_review: '領養申請審核中',
    rehome_application_received: '收到新的領養申請',
    animal_status_changed: '動物狀態更新',
    system_notification: '系統通知',
  }
  return titleMap[type] || '通知'
}

// 獲取通知顏色
const getNotificationColor = (type: string): string => {
  const colorMap: Record<string, string> = {
    application_submitted: 'bg-blue-500',
    application_approved: 'bg-green-500',
    application_rejected: 'bg-red-500',
    application_under_review: 'bg-yellow-500',
    rehome_application_received: 'bg-purple-500',
    animal_status_changed: 'bg-indigo-500',
    system_notification: 'bg-gray-500',
  }
  return colorMap[type] || 'bg-gray-500'
}

// 獲取通知圖示 (SVG path)
const getNotificationIcon = (type: string): string => {
  const iconMap: Record<string, string> = {
    application_submitted: '<path d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>',
    application_approved: '<path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>',
    application_rejected: '<path d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/>',
    application_under_review: '<path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>',
    rehome_application_received: '<path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>',
    animal_status_changed: '<path d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>',
    system_notification: '<path d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>',
  }
  return iconMap[type] || iconMap.system_notification
}

// 生命週期
onMounted(async () => {
  await fetchNotifications()
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>
