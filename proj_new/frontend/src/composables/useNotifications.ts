import { ref, computed } from 'vue'
import api from '@/api/client'

export interface Notification {
  notification_id: number
  recipient_id: number
  actor_id: number | null
  type: string
  payload: Record<string, any>
  read: boolean
  created_at: string
  read_at: string | null
}

export function useNotifications() {
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 輪詢間隔（毫秒）
  const POLL_INTERVAL = 30000 // 30 秒
  let pollTimer: number | null = null

  /**
   * 取得通知列表
   */
  const fetchNotifications = async (readFilter?: boolean) => {
    loading.value = true
    error.value = null

    try {
      const params: Record<string, any> = {}
      if (readFilter !== undefined) {
        params.read = readFilter
      }

      const response = await api.get<{
        notifications: Notification[]
        total: number
      }>('/notifications', { params })

      notifications.value = response.data.notifications
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || '載入通知失敗'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * 取得未讀數量
   */
  const fetchUnreadCount = async () => {
    try {
      const response = await api.get<{ unread_count: number }>('/notifications/unread-count')
      unreadCount.value = response.data.unread_count
      return response.data.unread_count
    } catch (err: any) {
      console.error('Failed to fetch unread count:', err)
      return 0
    }
  }

  /**
   * 標記單個通知為已讀
   */
  const markAsRead = async (notificationId: number) => {
    try {
      const response = await api.post<Notification>(
        `/notifications/${notificationId}/mark-read`
      )

      // 更新本地狀態
      const index = notifications.value.findIndex(
        (n) => n.notification_id === notificationId
      )
      if (index !== -1) {
        notifications.value[index] = response.data
      }

      // 更新未讀數量
      if (!response.data.read) {
        unreadCount.value = Math.max(0, unreadCount.value - 1)
      }

      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || '標記已讀失敗'
      throw err
    }
  }

  /**
   * 標記所有通知為已讀
   */
  const markAllAsRead = async () => {
    try {
      const response = await api.post<{
        message: string
        updated_count: number
      }>('/notifications/mark-all-read')

      // 更新本地狀態
      notifications.value.forEach((n) => {
        n.read = true
      })

      unreadCount.value = 0

      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || '標記全部已讀失敗'
      throw err
    }
  }

  /**
   * 刪除通知
   */
  const deleteNotification = async (notificationId: number) => {
    try {
      await api.delete(`/notifications/${notificationId}`)

      // 從列表中移除
      const index = notifications.value.findIndex(
        (n) => n.notification_id === notificationId
      )
      if (index !== -1) {
        const wasUnread = !notifications.value[index].read
        notifications.value.splice(index, 1)

        if (wasUnread) {
          unreadCount.value = Math.max(0, unreadCount.value - 1)
        }
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || '刪除通知失敗'
      throw err
    }
  }

  /**
   * 開始輪詢通知
   */
  const startPolling = () => {
    // 立即執行一次
    fetchUnreadCount()

    // 設置定時輪詢
    if (pollTimer) {
      clearInterval(pollTimer)
    }

    pollTimer = window.setInterval(() => {
      fetchUnreadCount()
    }, POLL_INTERVAL)
  }

  /**
   * 停止輪詢
   */
  const stopPolling = () => {
    if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
  }

  /**
   * 取得通知顯示文字
   */
  const getNotificationMessage = (notification: Notification): string => {
    const { type, payload } = notification

    switch (type) {
      case 'application_submitted':
        return `您的申請已提交：${payload.animal_name || '動物'}`
      case 'application_approved':
        return `您的申請已通過：${payload.animal_name || '動物'}`
      case 'application_rejected':
        return `您的申請已被拒絕：${payload.animal_name || '動物'}`
      case 'animal_published':
        return `您的動物已發布：${payload.animal_name || ''}`
      case 'animal_retired':
        return `動物已下架：${payload.animal_name || ''}`
      default:
        return payload.message || '您有新通知'
    }
  }

  // 計算屬性
  const unreadNotifications = computed(() =>
    notifications.value.filter((n) => !n.read)
  )

  const readNotifications = computed(() =>
    notifications.value.filter((n) => n.read)
  )

  return {
    // 狀態
    notifications,
    unreadCount,
    loading,
    error,

    // 計算屬性
    unreadNotifications,
    readNotifications,

    // 方法
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification,
    startPolling,
    stopPolling,
    getNotificationMessage,
  }
}
