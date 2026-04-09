<template>
  <div class="max-w-lg mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">個人資料</h1>
    <div class="bg-white rounded-xl shadow-sm p-6">
      <div class="flex items-center gap-4 mb-6">
        <img v-if="authStore.user?.avatar" :src="authStore.user.avatar" :alt="authStore.user.name"
          class="w-16 h-16 rounded-full" />
        <div class="w-16 h-16 rounded-full bg-primary-100 flex items-center justify-center text-2xl" v-else>
          {{ authStore.user?.name?.[0] }}
        </div>
        <div>
          <p class="font-semibold text-lg">{{ authStore.user?.name }}</p>
          <p class="text-gray-400 text-sm">LINE 登入</p>
        </div>
      </div>
      <div class="space-y-4">
        <div>
          <label class="text-sm font-medium text-gray-600 block mb-1">姓名</label>
          <input v-model="form.name" type="text"
            class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-400" />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-600 block mb-1">Email</label>
          <input v-model="form.email" type="email"
            class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-400" />
        </div>
        <div>
          <label class="text-sm font-medium text-gray-600 block mb-1">手機</label>
          <input v-model="form.phone" type="tel"
            class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-400" />
        </div>
      </div>
      <button @click="save" :disabled="saving"
        class="w-full mt-6 bg-primary-500 hover:bg-primary-600 text-white font-semibold py-3 rounded-xl disabled:opacity-50">
        {{ saving ? '儲存中...' : '儲存變更' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import api from '@/api'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const saving = ref(false)
const form = reactive({ name: '', email: '', phone: '' })

onMounted(() => {
  form.name = authStore.user?.name || ''
  form.email = authStore.user?.email || ''
  form.phone = authStore.user?.phone || ''
})

async function save() {
  saving.value = true
  try {
    await api.patch('/api/v1/users/me', form)
    await authStore.fetchUser()
    alert('已儲存')
  } finally {
    saving.value = false
  }
}
</script>
