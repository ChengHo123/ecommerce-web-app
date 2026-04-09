<template>
  <div class="min-h-screen flex items-center justify-center">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-blue-500 border-t-transparent mx-auto mb-4"></div>
      <p class="text-gray-600">驗證中...</p>
      <p v-if="error" class="text-red-500 mt-2">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminAuthStore } from '@/stores/auth'
import api from '@/api'

const router = useRouter()
const authStore = useAdminAuthStore()
const error = ref('')

onMounted(async () => {
  const params = new URLSearchParams(window.location.search)
  const code = params.get('code')
  const state = params.get('state')
  const savedState = sessionStorage.getItem('admin_line_state')

  if (!code || state !== savedState) {
    error.value = '驗證失敗'
    setTimeout(() => router.push('/login'), 2000)
    return
  }

  try {
    const { data } = await api.get(`/api/v1/auth/line/callback`, {
      params: { code, state, redirect_uri: 'http://localhost:5174/auth/line/callback' }
    })
    authStore.setToken(data.access_token)
    await authStore.fetchUser()
    if (authStore.isLoggedIn) {
      router.push('/dashboard')
    } else {
      error.value = '此帳號無管理員權限'
      setTimeout(() => router.push('/login'), 2000)
    }
  } catch {
    error.value = '登入失敗'
    setTimeout(() => router.push('/login'), 2000)
  }
})
</script>
