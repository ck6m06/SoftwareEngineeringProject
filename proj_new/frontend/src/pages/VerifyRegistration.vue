<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
    <div class="max-w-md w-full space-y-8">
      <div class="bg-white p-8 rounded shadow">
        <h2 class="text-2xl font-bold mb-4">輸入驗證碼</h2>
        <p class="text-sm text-gray-600 mb-4">已將驗證碼寄至：{{ maskedEmail }}</p>

        <div v-if="message" :class="messageClass" class="p-3 rounded mb-4">{{ message }}</div>

        <form @submit.prevent="submitCode" class="space-y-4">
          <input v-model="code" maxlength="6" placeholder="輸入 6 位驗證碼" class="w-full px-3 py-2 border rounded" />

          <div class="flex items-center justify-between">
            <button :disabled="loading" class="px-4 py-2 bg-blue-600 text-white rounded">驗證</button>
            <button type="button" @click="resend" :disabled="resending" class="text-sm text-blue-600">{{ resending ? '發送中...' : '重新發送驗證碼' }}</button>
          </div>
        </form>

        <div class="mt-4 text-sm text-gray-500">
          <router-link to="/login">返回登入</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/client'

const route = useRoute()
const router = useRouter()

const pendingId = Number(route.query.pending_id || 0)
const maskedEmail = String(route.query.masked || '')

const code = ref('')
const loading = ref(false)
const resending = ref(false)
const message = ref('')
const messageClass = ref('bg-green-50 text-green-700')

async function submitCode() {
  if (!pendingId || !code.value) return
  loading.value = true
  message.value = ''
  try {
    await api.post('/auth/verify-registration', { pending_id: pendingId, code: code.value })
    message.value = '驗證成功，請使用您的帳號登入' 
    messageClass.value = 'bg-green-50 text-green-700'
    setTimeout(() => router.push('/login'), 2000)
  } catch (err: any) {
    message.value = err.response?.data?.message || '驗證失敗'
    messageClass.value = 'bg-red-50 text-red-700'
  } finally {
    loading.value = false
  }
}

async function resend() {
  if (!pendingId) return
  resending.value = true
  try {
    await api.post('/auth/resend-registration-code', { pending_id: pendingId })
    message.value = '驗證碼已重新發送' 
    messageClass.value = 'bg-green-50 text-green-700'
  } catch (err: any) {
    message.value = err.response?.data?.message || '重新發送失敗'
    messageClass.value = 'bg-red-50 text-red-700'
  } finally {
    resending.value = false
  }
}
</script>

<style scoped>
.bg-green-50 { padding: 8px; }
.bg-red-50 { padding: 8px; }
</style>
