<template>
  <div class="min-h-screen flex items-center justify-center">
    <div class="text-center">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent mx-auto mb-4"></div>
      <p class="text-gray-600">正在登入...</p>
      <p v-if="error" class="text-red-500 mt-2">{{ error }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'
import api from '@/api'

const router = useRouter()
const authStore = useAuthStore()
const cartStore = useCartStore()
const error = ref('')

onMounted(async () => {
  const params = new URLSearchParams(window.location.search)
  const code = params.get('code')
  const state = params.get('state')
  const savedState = sessionStorage.getItem('line_state')

  if (!code || state !== savedState) {
    error.value = '驗證失敗，請重新登入'
    setTimeout(() => router.push('/login'), 2000)
    return
  }

  try {
    const { data } = await api.get(`/api/v1/auth/line/callback?code=${code}&state=${state}`)
    authStore.setTokens(data.access_token, data.refresh_token)
    await authStore.fetchUser()
    await cartStore.fetchCart()

    const redirect = sessionStorage.getItem('redirect_after_login') || '/'
    sessionStorage.removeItem('line_state')
    sessionStorage.removeItem('redirect_after_login')
    router.push(redirect)
  } catch {
    error.value = '登入失敗，請稍後再試'
    setTimeout(() => router.push('/login'), 2000)
  }
})
</script>
