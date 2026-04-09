<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="bg-white rounded-2xl shadow-lg p-8 w-full max-w-sm">
      <h1 class="text-2xl font-bold text-center mb-2">後台管理</h1>
      <p class="text-center text-gray-400 text-sm mb-8">僅限管理員登入</p>
      <button @click="loginWithLine" :disabled="loading"
        class="w-full flex items-center justify-center gap-3 bg-[#06C755] hover:bg-[#05b34b] text-white font-semibold py-3 px-6 rounded-xl disabled:opacity-60">
        使用 LINE 登入
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '@/api'
import { useAdminAuthStore } from '@/stores/auth'

const authStore = useAdminAuthStore()
const loading = ref(false)

async function loginWithLine() {
  loading.value = true
  try {
    const { data } = await api.get('/api/v1/auth/line/login-url', {
      params: { redirect_uri: 'http://localhost:5174/auth/line/callback' }
    })
    sessionStorage.setItem('admin_line_state', data.state)
    window.location.href = data.url
  } finally {
    loading.value = false
  }
}
</script>
