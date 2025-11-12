<template>
  <div class="relative">
    <!-- 通知鈴鐺按鈕 -->
    <button
      @click.stop="toggleDropdown"
      class="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 rounded-full"
      aria-label="通知"
    >
      <svg
        class="h-6 w-6"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
        />
      </svg>

      <!-- 未讀數量 Badge -->
      <span
        v-if="unreadCount > 0"
        class="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full"
      >
        {{ unreadCount > 99 ? '99+' : unreadCount }}
      </span>
    </button>

    <!-- 下拉選單 -->
    <Transition
      enter-active-class="transition ease-out duration-200"
      enter-from-class="transform opacity-0 scale-95"
      enter-to-class="transform opacity-100 scale-100"
      leave-active-class="transition ease-in duration-75"
      leave-from-class="transform opacity-100 scale-100"
      leave-to-class="transform opacity-0 scale-95"
    >
      <div
        v-if="showDropdown"
        v-click-outside="closeDropdown"
        class="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg ring-1 ring-black ring-opacity-5 z-50"
      >
        <!-- 標題列 -->
        <div class="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-sm font-semibold text-gray-900">通知</h3>
          <button
            v-if="unreadNotifications.length > 0"
            @click="handleMarkAllAsRead"
            class="text-xs text-indigo-600 hover:text-indigo-500"
          >
            全部已讀
          </button>
        </div>

        <!-- 通知列表 -->
        <div class="max-h-96 overflow-y-auto">
          <!-- Loading -->
          <div v-if="loading" class="px-4 py-8 text-center text-gray-500">
            <svg class="animate-spin h-5 w-5 mx-auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>

          <!-- 空狀態 -->
          <div v-else-if="notifications.length === 0" class="px-4 py-8 text-center text-gray-500">
            <svg class="h-12 w-12 mx-auto mb-2 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
            </svg>
            <p class="text-sm">目前沒有通知</p>
          </div>

          <!-- 通知項目 -->
          <div v-else>
            <div
              v-for="notification in notifications"
              :key="notification.notification_id"
              :class="[
                'px-4 py-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0',
                !notification.read && 'bg-blue-50'
              ]"
              @click="handleNotificationClick(notification)"
            >
              <div class="flex items-start">
                <!-- 未讀指示器 -->
                <div class="flex-shrink-0 mt-1">
                  <span
                    v-if="!notification.read"
                    class="inline-block h-2 w-2 rounded-full bg-blue-600"
                  ></span>
                  <span
                    v-else
                    class="inline-block h-2 w-2 rounded-full bg-gray-300"
                  ></span>
                </div>

                <!-- 內容 -->
                <div class="ml-3 flex-1 min-w-0">
                  <p class="text-sm text-gray-900">
                    {{ getNotificationMessage(notification) }}
                  </p>
                  <p class="text-xs text-gray-500 mt-1">
                    {{ formatDate(notification.created_at) }}
                  </p>
                </div>

                <!-- 刪除按鈕 -->
                <button
                  @click.stop="handleDelete(notification.notification_id)"
                  class="ml-2 text-gray-400 hover:text-gray-600"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部連結 -->
        <div class="px-4 py-3 border-t border-gray-200 text-center">
          <router-link
            to="/notifications"
            class="text-sm text-indigo-600 hover:text-indigo-500"
            @click="closeDropdown"
          >
            查看所有通知
          </router-link>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useNotifications } from '@/composables/useNotifications'
import { formatDistanceToNow } from 'date-fns'
import { zhTW } from 'date-fns/locale'

const showDropdown = ref(false)

const {
  notifications,
  unreadCount,
  unreadNotifications,
  loading,
  fetchNotifications,
  markAsRead,
  markAllAsRead,
  deleteNotification,
  startPolling,
  stopPolling,
  getNotificationMessage,
} = useNotifications()

// 切換下拉選單
const toggleDropdown = async () => {
  showDropdown.value = !showDropdown.value

  if (showDropdown.value) {
    await fetchNotifications()
  }
}

// 關閉下拉選單
const closeDropdown = () => {
  showDropdown.value = false
}

// 點擊通知
const handleNotificationClick = async (notification: any) => {
  if (!notification.read) {
    await markAsRead(notification.notification_id)
  }
  // TODO: 根據通知類型導航到相應頁面
  closeDropdown()
}

// 標記全部已讀
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

// Click outside directive
const vClickOutside = {
  mounted(el: any, binding: any) {
    el.clickOutsideEvent = (event: Event) => {
      // 確保點擊不在元素內部
      if (!(el === event.target || el.contains(event.target as Node))) {
        binding.value()
      }
    }
    // 使用 setTimeout 延遲註冊事件,避免與 toggleDropdown 衝突
    setTimeout(() => {
      document.addEventListener('click', el.clickOutsideEvent)
    }, 0)
  },
  unmounted(el: any) {
    if (el.clickOutsideEvent) {
      document.removeEventListener('click', el.clickOutsideEvent)
    }
  },
}

// 生命週期
onMounted(() => {
  startPolling()
})

onUnmounted(() => {
  stopPolling()
})
</script>
