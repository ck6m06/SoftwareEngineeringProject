<template>
  <div v-if="visible" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-white rounded-lg shadow-lg w-full max-w-md p-6">
      <h3 class="text-lg font-semibold mb-2">輸入驗證碼</h3>
      <p class="text-sm text-gray-600 mb-4">已將驗證碼寄至：{{ maskedEmail }}</p>

      <div v-if="message" :class="messageClass" class="p-3 rounded mb-4">{{ message }}</div>

      <form @submit.prevent="submitCode" class="space-y-4">
        <input v-model="code" maxlength="6" placeholder="輸入 6 位驗證碼" class="w-full px-3 py-2 border rounded" />

        <div class="flex items-center justify-between">
          <button :disabled="loading" class="px-4 py-2 bg-blue-600 text-white rounded">{{ loading ? '驗證中...' : '驗證' }}</button>
          <button type="button" @click="resend" :disabled="resending" class="text-sm text-blue-600">{{ resending ? '發送中...' : '重新發送驗證碼' }}</button>
        </div>
      </form>

      <div class="mt-4 text-right">
        <button @click="$emit('close')" class="text-sm text-gray-600">關閉</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import api from '@/api/client'

defineProps<{ visible: boolean; pendingId: number | string; maskedEmail: string }>()
const emit = defineEmits(['close', 'verified'])

const props = defineProps<any>()
const code = ref('')
const loading = ref(false)
const resending = ref(false)
const message = ref('')
const messageClass = ref('bg-green-50 text-green-700')

async function submitCode() {
  if (!props.pendingId || !code.value) return
  loading.value = true
  message.value = ''
  try {
    await api.post('/auth/verify-registration', { pending_id: Number(props.pendingId), code: code.value })
    message.value = '驗證成功，將導向登入頁'
    messageClass.value = 'bg-green-50 text-green-700'
    // 通知父元件驗證成功
    emit('verified')
  } catch (err: any) {
    message.value = err.response?.data?.message || '驗證失敗'
    messageClass.value = 'bg-red-50 text-red-700'
  } finally {
    loading.value = false
  }
}

async function resend() {
  if (!props.pendingId) return
  resending.value = true
  try {
    await api.post('/auth/resend-registration-code', { pending_id: Number(props.pendingId) })
    message.value = '驗證碼已重新發送'
    messageClass.value = 'bg-green-50 text-green-700'
  } catch (err: any) {
    message.value = err.response?.data?.message || '重新發送失敗'
    messageClass.value = 'bg-red-50 text-red-700'
  } finally {
    resending.value = false
  }
}

// 當 modal 打開時清空欄位
watch(() => props.visible, (v) => {
  if (v) {
    code.value = ''
    message.value = ''
  }
})
</script>

<style scoped>
.bg-green-50 { padding: 8px; }
.bg-red-50 { padding: 8px; }
</style>
