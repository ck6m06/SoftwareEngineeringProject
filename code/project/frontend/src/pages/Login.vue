<template>
  <div class="login-page min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          登入您的帳號
        </h2>
      </div>
      <div class="mt-8 bg-white py-8 px-6 shadow rounded-lg">
  <form class="space-y-6" @submit.prevent="handleLogin">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">
              Email
            </label>
            <input
              id="email"
              v-model="email"
              type="email"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              密碼
            </label>
            <input
              id="password"
              v-model="password"
              type="password"
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
            <div class="mt-1 text-right">
              <router-link to="/forgot-password" class="text-xs text-blue-600 hover:text-blue-500">
                忘記密碼？
              </router-link>
            </div>
          </div>

          <div>
            <button
              type="submit"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              登入
            </button>
          </div>

          <!-- 未驗證 Email 的提示與重發按鈕 -->
          <div v-if="unverifiedEmail" class="mt-4 bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded">
            <p class="text-sm">您的 Email 還未完成驗證 ({{ unverifiedEmail }}），請點選下方按鈕重新發送驗證郵件或檢查收件匣。</p>
            <div class="mt-3 flex gap-2">
              <button
                type="button"
                @click="resendVerification"
                :disabled="resending"
                class="inline-flex items-center px-3 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
              >
                <svg v-if="resending" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
                </svg>
                {{ resending ? '發送中...' : '重新發送驗證郵件' }}
              </button>
              <router-link to="/verify-email" class="inline-flex items-center px-3 py-2 border border-gray-300 rounded-md text-sm text-gray-700 bg-white hover:bg-gray-50">輸入驗證連結</router-link>
            </div>
          </div>

          <div class="text-center">
            <router-link to="/register" class="text-sm text-blue-600 hover:text-blue-500">
              還沒有帳號？立即註冊
            </router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import api from '@/api/client'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')

const unverifiedEmail = ref('')
const resending = ref(false)

const handleLogin = async () => {
  unverifiedEmail.value = ''
  try {
    await authStore.login(email.value, password.value)
    router.push('/')
  } catch (error: any) {
    console.error('Login error:', error)

    // 若後端回 403 且訊息含有驗證相關文字，提示使用者重新發送驗證信
    if (error.response?.status === 403) {
      const msg = error.response?.data?.message || ''
      if (msg.includes('驗證') || msg.includes('驗證 Email')) {
        unverifiedEmail.value = email.value
        return
      }
    }

    // 其餘錯誤顯示通用訊息
    alert(error.response?.data?.message || '登入失敗，請檢查您的帳號密碼')
  }
}

async function resendVerification() {
  if (!unverifiedEmail.value) return
  resending.value = true
  try {
    await api.post('/auth/resend-verification', { email: unverifiedEmail.value })
    alert('驗證郵件已重新發送，請查看您的收件匣（含垃圾信件）')
  } catch (err: any) {
    console.error('Resend error:', err)
    alert(err.response?.data?.message || '重新發送失敗，請稍後再試')
  } finally {
    resending.value = false
  }
}
</script>
