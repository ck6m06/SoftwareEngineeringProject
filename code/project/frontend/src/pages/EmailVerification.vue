<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full">
      <!-- 載入中狀態 -->
      <div v-if="status === 'loading'" class="bg-white rounded-lg shadow-xl p-8 text-center">
        <div class="flex justify-center mb-6">
          <svg class="animate-spin h-16 w-16 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">驗證中...</h2>
        <p class="text-gray-600">請稍候，正在驗證您的 Email</p>
      </div>

      <!-- 驗證成功 -->
      <div v-else-if="status === 'success'" class="bg-white rounded-lg shadow-xl p-8 text-center">
        <div class="flex justify-center mb-6">
          <div class="rounded-full bg-green-100 p-3">
            <svg class="h-16 w-16 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">✅ Email 驗證成功!</h2>
        <p class="text-gray-600 mb-6">您的帳號已啟用，{{ countdown }} 秒後自動跳轉至登入頁</p>
        
        <div class="space-y-3">
          <button
            @click="goToLogin"
            class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition"
          >
            立即前往登入
          </button>
          <button
            @click="goToHome"
            class="w-full flex justify-center py-3 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition"
          >
            返回首頁
          </button>
        </div>
      </div>

      <!-- 驗證失敗 -->
      <div v-else-if="status === 'error'" class="bg-white rounded-lg shadow-xl p-8 text-center">
        <div class="flex justify-center mb-6">
          <div class="rounded-full bg-red-100 p-3">
            <svg class="h-16 w-16 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">❌ 驗證失敗</h2>
        <p class="text-red-600 mb-6">{{ errorMessage }}</p>
        
        <div class="space-y-3">
          <button
            @click="resendVerification"
            :disabled="resending"
            class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            <svg v-if="resending" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ resending ? '發送中...' : '重新發送驗證郵件' }}
          </button>
          <button
            @click="goToLogin"
            class="w-full flex justify-center py-3 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition"
          >
            返回登入
          </button>
        </div>
      </div>

      <!-- 已驗證過 -->
      <div v-else-if="status === 'already_verified'" class="bg-white rounded-lg shadow-xl p-8 text-center">
        <div class="flex justify-center mb-6">
          <div class="rounded-full bg-blue-100 p-3">
            <svg class="h-16 w-16 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </div>
        </div>
        <h2 class="text-2xl font-bold text-gray-900 mb-2">ℹ️ Email 已驗證</h2>
        <p class="text-gray-600 mb-6">您的帳號已經完成驗證，可以直接登入使用</p>
        
        <button
          @click="goToLogin"
          class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition"
        >
          前往登入
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/client'

const route = useRoute()
const router = useRouter()

const status = ref<'loading' | 'success' | 'error' | 'already_verified'>('loading')
const errorMessage = ref('')
const countdown = ref(3)
const resending = ref(false)

let countdownInterval: number | undefined

onMounted(async () => {
  const token = route.query.token as string

  if (!token) {
    status.value = 'error'
    errorMessage.value = '缺少驗證 token，請檢查郵件中的連結是否完整'
    return
  }

  try {
    // 呼叫驗證 API
    const response = await api.get(`/auth/verify?token=${token}`)
    
    if (response.data.message?.includes('已經驗證')) {
      status.value = 'already_verified'
    } else {
      status.value = 'success'
      startCountdown()
    }
  } catch (error: any) {
    status.value = 'error'
    
    if (error.response?.data?.message) {
      errorMessage.value = error.response.data.message
    } else if (error.response?.status === 400) {
      errorMessage.value = '驗證 token 無效或已過期，請重新發送驗證郵件'
    } else if (error.response?.status === 404) {
      errorMessage.value = '找不到對應的使用者帳號'
    } else {
      errorMessage.value = '驗證過程發生錯誤，請稍後再試'
    }
  }
})

// 開始倒數計時
function startCountdown() {
  countdownInterval = window.setInterval(() => {
    countdown.value--
    
    if (countdown.value <= 0) {
      clearInterval(countdownInterval)
      goToLogin()
    }
  }, 1000)
}

// 前往登入頁
function goToLogin() {
  if (countdownInterval) {
    clearInterval(countdownInterval)
  }
  router.push('/login')
}

// 返回首頁
function goToHome() {
  if (countdownInterval) {
    clearInterval(countdownInterval)
  }
  router.push('/')
}

// 重新發送驗證郵件
async function resendVerification() {
  resending.value = true
  
  try {
    // 需要用戶輸入 email
    const email = prompt('請輸入您的註冊 Email:')
    
    if (!email) {
      resending.value = false
      return
    }
    
    await api.post('/auth/resend-verification', { email })
    
    alert('驗證郵件已重新發送，請查看您的信箱')
    status.value = 'loading'
    errorMessage.value = ''
  } catch (error: any) {
    alert(error.response?.data?.message || '重新發送失敗，請稍後再試')
  } finally {
    resending.value = false
  }
}
</script>

<style scoped>
/* 動畫效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.bg-white {
  animation: fadeIn 0.5s ease-out;
}
</style>