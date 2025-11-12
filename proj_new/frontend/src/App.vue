<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <Navbar />
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import Navbar from '@/components/layout/Navbar.vue'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 應用啟動時恢復登入狀態
onMounted(() => {
  // 如果有 token 但沒有 user 資料,則重新獲取
  if (authStore.accessToken && !authStore.user) {
    authStore.fetchCurrentUser()
  }
})
</script>

<style scoped>
</style>
