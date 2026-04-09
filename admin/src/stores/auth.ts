import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'

interface AdminUser {
  id: number
  name: string
  email: string | null
  role: string
}

export const useAdminAuthStore = defineStore('adminAuth', () => {
  const user = ref<AdminUser | null>(null)
  const token = ref<string | null>(localStorage.getItem('admin_access_token'))
  const isLoggedIn = computed(() => !!token.value && !!user.value)

  async function fetchUser() {
    if (!token.value) return
    try {
      const { data } = await api.get('/api/v1/users/me')
      if (data.role !== 'admin') throw new Error('Not admin')
      user.value = data
    } catch {
      logout()
    }
  }

  function setToken(t: string) {
    token.value = t
    localStorage.setItem('admin_access_token', t)
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('admin_access_token')
  }

  return { user, token, isLoggedIn, fetchUser, setToken, logout }
})
