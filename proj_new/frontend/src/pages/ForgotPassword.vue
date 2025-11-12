<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- 標題 -->
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
          忘記密碼
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600">
          輸入您的 email，我們將發送重置密碼的連結
        </p>
      </div>

      <!-- 表單 -->
      <form v-if="!success" class="mt-8 space-y-6" @submit.prevent="handleSubmit">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="email" class="sr-only">Email</label>
            <input
              id="email"
              v-model="email"
              name="email"
              type="email"
              required
              class="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="Email 地址"
              :disabled="loading"
            />
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
            :disabled="loading"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            <span v-if="loading">
              <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            <span v-else>發送重置連結</span>
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

      <!-- 成功訊息 -->
      <div v-else class="rounded-md bg-green-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <h3 class="text-sm font-medium text-green-800">郵件已發送</h3>
            <div class="mt-2 text-sm text-green-700">
              <p>如果該 email 存在於系統中，您將收到密碼重置連結。</p>
              <p class="mt-2">請檢查您的郵箱（包括垃圾郵件資料夾）。</p>
            </div>
          </div>
        </div>
        <div class="mt-4">
          <router-link
            to="/login"
            class="text-sm font-medium text-indigo-600 hover:text-indigo-500"
          >
            返回登入頁面
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '@/api/client'

const email = ref('')
const loading = ref(false)
const error = ref('')
const success = ref(false)

const handleSubmit = async () => {
  if (!email.value) {
    error.value = '請輸入 Email'
    return
  }

  loading.value = true
  error.value = ''

  try {
    await api.post('/auth/forgot-password', {
      email: email.value
    })

    success.value = true
  } catch (err: any) {
    error.value = err.response?.data?.message || '發送失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}
</script>
