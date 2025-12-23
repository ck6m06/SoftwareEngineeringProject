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
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
            <p v-if="errors.username" class="mt-1 text-sm text-red-600">{{ errors.username }}</p>
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
                required
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              <p v-if="errors.first_name" class="mt-1 text-sm text-red-600">{{ errors.first_name }}</p>
            </div>
            <div>
              <label for="lastName" class="block text-sm font-medium text-gray-700">
                姓氏
              </label>
              <input
                id="lastName"
                v-model="form.last_name"
                type="text"
                required
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
              <p v-if="errors.last_name" class="mt-1 text-sm text-red-600">{{ errors.last_name }}</p>
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
              required
              class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
            <p v-if="errors.phone_number" class="mt-1 text-sm text-red-600">{{ errors.phone_number }}</p>
          </div>

          <!-- Region (required) -->
          <div>
            <label for="region" class="block text-sm font-medium text-gray-700">地區 *</label>
            <select
              id="region"
              v-model="form.region"
              required
              class="mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              :class="errors.region ? 'border-red-300' : 'border-gray-300'"
            >
              <option value="">請選擇地區</option>
              <option>基隆市</option>
              <option>台北市</option>
              <option>新北市</option>
              <option>桃園市</option>
              <option>台中市</option>
              <option>台南市</option>
              <option>高雄市</option>
              <option>新竹市</option>
              <option>苗栗縣</option>
              <option>彰化縣</option>
              <option>南投縣</option>
              <option>雲林縣</option>
              <option>嘉義市</option>
              <option>嘉義縣</option>
              <option>屏東縣</option>
              <option>宜蘭縣</option>
              <option>花蓮縣</option>
              <option>台東縣</option>
              <option>澎湖縣</option>
              <option>金門縣</option>
              <option>連江縣</option>
            </select>
            <p v-if="errors.region" class="mt-1 text-sm text-red-600">{{ errors.region }}</p>
          </div>

          <!-- Account Type (個人 / 收容所) -->
          <div>
            <label for="role" class="block text-sm font-medium text-gray-700">帳號類型 *</label>
            <select
              id="role"
              v-model="form.role"
              required
              class="mt-1 block w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              :class="errors.role ? 'border-red-300' : 'border-gray-300'"
            >
              <option value="GENERAL_MEMBER">個人</option>
              <option value="SHELTER_MEMBER">收容所</option>
            </select>
            <p v-if="errors.role" class="mt-1 text-sm text-red-600">{{ errors.role }}</p>
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
  region: '',
  role: 'GENERAL_MEMBER',
})

const errors = reactive({
  email: '',
  password: '',
  confirmPassword: '',
  region: '',
  role: '',
  username: '',
  first_name: '',
  last_name: '',
  phone_number: '',
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

  errors.region = ''
  errors.role = ''
  errors.username = ''
  errors.first_name = ''
  errors.last_name = ''
  errors.phone_number = ''

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

  // 使用者名稱必填
  if (!form.username || !form.username.trim()) {
    errors.username = '請輸入使用者名稱'
    isValid = false
  }

  // 名字/姓氏必填
  if (!form.first_name || !form.first_name.trim()) {
    errors.first_name = '請輸入名字'
    isValid = false
  }
  if (!form.last_name || !form.last_name.trim()) {
    errors.last_name = '請輸入姓氏'
    isValid = false
  }

  // 電話號碼必填 (基本格式檢查)
  const phoneRegex = /^\+?[0-9\s\-()]{7,20}$/
  if (!form.phone_number || !phoneRegex.test(form.phone_number)) {
    errors.phone_number = '請輸入有效的電話號碼'
    isValid = false
  }

  // 地區必填
  if (!form.region) {
    errors.region = '請選擇地區'
    isValid = false
  }

  // 帳號類型必填
  if (!form.role) {
    errors.role = '請選擇帳號類型'
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
  if (form.region) registerData.region = form.region
  if (form.role) registerData.role = form.role

    const resp = await authStore.register(registerData)

    // debug: 印出後端回應到瀏覽器 console
    // eslint-disable-next-line no-console
    console.log('register response:', resp)

  // 導向驗證頁面（使用後端回傳的 pending_id / masked_email，若無則使用遮蔽 email）
  const pendingId = resp?.pending_id || ''
  const masked = resp?.masked_email || maskEmail(form.email)
  router.push({ name: 'VerifyRegistration', query: { pending_id: pendingId, masked, role: form.role } })
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
