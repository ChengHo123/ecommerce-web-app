import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'
import type { User } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const accessToken = ref<string | null>(localStorage.getItem('access_token'))

  const isLoggedIn = computed(() => !!accessToken.value && !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function fetchUser() {
    if (!accessToken.value) return
    try {
      const { data } = await api.get('/api/v1/users/me')
      user.value = data
    } catch {
      logout()
    }
  }

  function setTokens(access: string, refresh: string) {
    accessToken.value = access
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  function logout() {
    user.value = null
    accessToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  function getLineLoginUrl() {
    return api.get('/api/v1/auth/line/login-url')
  }

  return { user, accessToken, isLoggedIn, isAdmin, fetchUser, setTokens, logout, getLineLoginUrl }
})
