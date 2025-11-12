/**
 * Auth Store - 身份驗證狀態管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/client'
import type { User } from '@/types/models'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(
    localStorage.getItem('user') ? JSON.parse(localStorage.getItem('user')!) : null
  )
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'ADMIN')
  const isShelterMember = computed(() => user.value?.role === 'SHELTER_MEMBER')

  // Actions
  async function login(email: string, password: string) {
    const response = await api.post('/auth/login', { email, password })
    
    const { access_token, refresh_token, user: userData } = response.data
    
    accessToken.value = access_token
    refreshToken.value = refresh_token
    user.value = userData
    
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    localStorage.setItem('user', JSON.stringify(userData))
  }

  async function register(data: {
    email: string
    password: string
    username?: string
    first_name?: string
    last_name?: string
    phone_number?: string
  }) {
    const response = await api.post('/auth/register', data)
    return response.data
  }

  async function logout() {
    try {
      await api.post('/auth/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      accessToken.value = null
      refreshToken.value = null
      user.value = null
      
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  }

  async function fetchCurrentUser() {
    if (!accessToken.value) return

    try {
      const response = await api.get('/auth/me')
      user.value = response.data
      localStorage.setItem('user', JSON.stringify(response.data))
    } catch (error) {
      console.error('Fetch user error:', error)
      logout()
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) {
      throw new Error('No refresh token available')
    }

    try {
      const response = await api.post('/auth/refresh', {}, {
        headers: {
          Authorization: `Bearer ${refreshToken.value}`
        }
      })
      
      const { access_token } = response.data
      accessToken.value = access_token
      localStorage.setItem('access_token', access_token)
      
      return access_token
    } catch (error) {
      logout()
      throw error
    }
  }

  return {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    isAdmin,
    isShelterMember,
    login,
    register,
    logout,
    fetchCurrentUser,
    refreshAccessToken,
  }
})
