<template>
  <div class="register-page min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          註冊新帳號
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          加入我們，開始您的送養之旅
        </p>
      </div>

      <div class="mt-8 bg-white py-8 px-6 shadow rounded-lg">
        <form class="space-y-6" @submit.prevent="handleRegister">
          <!-- Email -->
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">
              Email *
            </label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              :class="errors.email ? 'border-red-300' : 'border-gray-300'"
            />
            <p v-if="errors.email" class="mt-1 text-sm text-red-600">{{ errors.email }}</p>
          </div>

          <!-- Password -->
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              密碼 *
            </label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              :class="errors.password ? 'border-red-300' : 'border-gray-300'"
            />
            <p v-if="errors.password" class="mt-1 text-sm text-red-600">{{ errors.password }}</p>
            <p class="mt-1 text-xs text-gray-500">至少 8 個字元，包含英文和數字</p>
          </div>

          <!-- Confirm Password -->
          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700">
              確認密碼 *
            </label>
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password"
              required
              class="mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              :class="errors.confirmPassword ? 'border-red-300' : 'border-gray-300'"
            />
            <p v-if="errors.confirmPassword" class="mt-1 text-sm text-red-600">{{ errors.confirmPassword }}</p>
          </div>

          <!-- Username -->
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700">
              使用者名稱
            </label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <!-- First Name & Last Name -->
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="firstName" class="block text-sm font-medium text-gray-700">
                名字
              </label>
              <input
                id="firstName"
                v-model="form.first_name"
                type="text"
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label for="lastName" class="block text-sm font-medium text-gray-700">
                姓氏
              </label>
              <input
                id="lastName"
                v-model="form.last_name"
                type="text"
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <!-- Phone Number -->
          <div>
            <label for="phoneNumber" class="block text-sm font-medium text-gray-700">
              電話號碼
            </label>
            <input
              id="phoneNumber"
              v-model="form.phone_number"
              type="tel"
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <!-- Error Message -->
          <div v-if="errorMessage" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative">
            {{ errorMessage }}
          </div>

          <!-- Success Message -->
          <div v-if="successMessage" class="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded relative">
            {{ successMessage }}
          </div>

          <!-- Submit Button -->
          <div>
            <button
              type="submit"
              :disabled="isLoading"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <span v-if="isLoading">註冊中...</span>
              <span v-else>註冊</span>
            </button>
          </div>

          <!-- Login Link -->
          <div class="text-center">
            <router-link to="/login" class="text-sm text-blue-600 hover:text-blue-500">
              已有帳號？立即登入
            </router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  email: '',
  password: '',
  confirmPassword: '',
  username: '',
  first_name: '',
  last_name: '',
  phone_number: '',
})

const errors = reactive({
  email: '',
  password: '',
  confirmPassword: '',
})

const isLoading = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

// no modal: navigate to VerifyRegistration page after register

// 驗證 Email 格式
function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// 驗證密碼強度
function validatePassword(password: string): boolean {
  // 至少 8 個字元，包含英文和數字
  return password.length >= 8 && /[a-zA-Z]/.test(password) && /[0-9]/.test(password)
}

// 表單驗證
function validateForm(): boolean {
  errors.email = ''
  errors.password = ''
  errors.confirmPassword = ''

  let isValid = true

  if (!validateEmail(form.email)) {
    errors.email = '請輸入有效的 Email 地址'
    isValid = false
  }

  if (!validatePassword(form.password)) {
    errors.password = '密碼至少 8 個字元，需包含英文和數字'
    isValid = false
  }

  if (form.password !== form.confirmPassword) {
    errors.confirmPassword = '密碼不一致'
    isValid = false
  }

  return isValid
}

// 將 email 做簡單遮蔽，例如 a***@domain.com
function maskEmail(email: string): string {
  try {
    const parts = email.split('@')
    if (parts.length !== 2) return email
    const local = parts[0]
    const domain = parts[1]
    if (local.length <= 2) {
      return `${local[0]}***@${domain}`
    }
    const maskedLocal = `${local[0]}${'*'.repeat(Math.max(1, local.length - 2))}${local.slice(-1)}`
    return `${maskedLocal}@${domain}`
  } catch (e) {
    return email
  }
}

// 處理註冊
async function handleRegister() {
  errorMessage.value = ''
  successMessage.value = ''

  if (!validateForm()) {
    return
  }

  isLoading.value = true

  try {
    const registerData: any = {
      email: form.email,
      password: form.password,
    }

    // 添加可選欄位
    if (form.username) registerData.username = form.username
    if (form.first_name) registerData.first_name = form.first_name
    if (form.last_name) registerData.last_name = form.last_name
    if (form.phone_number) registerData.phone_number = form.phone_number

    const resp = await authStore.register(registerData)

    // debug: 印出後端回應到瀏覽器 console
    // eslint-disable-next-line no-console
    console.log('register response:', resp)

  // 導向驗證頁面（使用後端回傳的 pending_id / masked_email，若無則使用遮蔽 email）
  const pendingId = resp?.pending_id || ''
  const masked = resp?.masked_email || maskEmail(form.email)
  router.push({ name: 'VerifyRegistration', query: { pending_id: pendingId, masked } })
  return
  } catch (error: any) {
    console.error('Register error:', error)
    
    if (error.response?.status === 409) {
      errorMessage.value = '此 Email 已被註冊'
    } else if (error.response?.data?.message) {
      errorMessage.value = error.response.data.message
    } else {
      errorMessage.value = '註冊失敗，請稍後再試'
    }
  } finally {
    isLoading.value = false
  }
}

// modal handlers removed (page-based verification flow is used)
</script>

<!-- removed duplicate modal block (modal is embedded in main template) -->
