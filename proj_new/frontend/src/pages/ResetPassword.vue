<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- 標題 -->
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          重置密碼
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          請輸入您的新密碼
        </p>
      </div>

      <!-- 表單 -->
      <form v-if="!success && !tokenError" class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="rounded-md shadow-sm space-y-4">
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">新密碼</label>
            <input
              id="password"
              v-model="password"
              name="password"
              type="password"
              required
              minlength="8"
              class="mt-1 appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="至少 8 個字符"
              :disabled="loading"
            />
          </div>

          <div>
            <label for="confirm-password" class="block text-sm font-medium text-gray-700">確認新密碼</label>
            <input
              id="confirm-password"
              v-model="confirmPassword"
              name="confirm-password"
              type="password"
              required
              minlength="8"
              class="mt-1 appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="再次輸入新密碼"
              :disabled="loading"
            />
          </div>
        </div>

        <!-- 密碼強度提示 -->
        <div v-if="password" class="text-sm">
          <p class="text-gray-600 mb-1">密碼強度：</p>
          <div class="space-y-1">
            <div :class="password.length >= 8 ? 'text-green-600' : 'text-gray-400'">
              ✓ 至少 8 個字符
            </div>
            <div :class="hasUpperCase ? 'text-green-600' : 'text-gray-400'">
              ✓ 包含大寫字母
            </div>
            <div :class="hasLowerCase ? 'text-green-600' : 'text-gray-400'">
              ✓ 包含小寫字母
            </div>
            <div :class="hasNumber ? 'text-green-600' : 'text-gray-400'">
              ✓ 包含數字
            </div>
          </div>
        </div>

        <!-- 錯誤訊息 -->
        <div v-if="error" class="rounded-md bg-red-50 p-4">
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm text-red-700">{{ error }}</p>
            </div>
          </div>
        </div>

        <!-- 提交按鈕 -->
        <div>
          <button
            type="submit"
            :disabled="loading || password !== confirmPassword"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            <span v-if="loading">
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            <span v-else>重置密碼</span>
          </button>
        </div>

        <!-- 返回登入 -->
        <div class="text-center">
          <router-link
            to="/login"
            class="text-sm font-medium text-indigo-600 hover:text-indigo-500"
          >
            返回登入頁面
          </router-link>
        </div>
      </form>

      <!-- Token 錯誤 -->
      <div v-else-if="tokenError" class="rounded-md bg-red-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-red-800">重置連結無效或已過期</h3>
            <div class="mt-2 text-sm text-red-700">
              <p>請重新申請密碼重置。</p>
            </div>
          </div>
        </div>
        <div class="mt-4 space-x-4">
          <router-link
            to="/forgot-password"
            class="text-sm font-medium text-indigo-600 hover:text-indigo-500"
          >
            重新申請重置
          </router-link>
          <router-link
            to="/login"
            class="text-sm font-medium text-indigo-600 hover:text-indigo-500"
          >
            返回登入
          </router-link>
        </div>
      </div>

      <!-- 成功訊息 -->
      <div v-else-if="success" class="rounded-md bg-green-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-green-800">密碼重置成功！</h3>
            <div class="mt-2 text-sm text-green-700">
              <p>您的密碼已成功更新，請使用新密碼登入。</p>
            </div>
          </div>
        </div>
        <div class="mt-4">
          <router-link
            to="/login"
            class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            前往登入
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/client'

const route = useRoute()

const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)
const tokenError = ref(false)

const token = computed(() => route.query.token as string)

// 密碼強度檢查
const hasUpperCase = computed(() => /[A-Z]/.test(password.value))
const hasLowerCase = computed(() => /[a-z]/.test(password.value))
const hasNumber = computed(() => /[0-9]/.test(password.value))

onMounted(() => {
  if (!token.value) {
    tokenError.value = true
  }
})

const handleSubmit = async () => {
  if (!password.value || !confirmPassword.value) {
    error.value = '請填寫所有欄位'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = '兩次輸入的密碼不一致'
    return
  }

  if (password.value.length < 8) {
    error.value = '密碼長度至少需要 8 個字符'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await api.post('/auth/reset-password', {
      token: token.value,
      new_password: password.value
    })

    success.value = true
  } catch (err: any) {
    if (err.response?.status === 400) {
      tokenError.value = true
    } else {
      error.value = err.response?.data?.message || '重置失敗，請稍後再試'
    }
  } finally {
    loading.value = false
  }
}
</script>
