<template>
  <div class="bg-white rounded-xl shadow-sm overflow-hidden">
    <table class="w-full text-sm">
      <thead class="bg-gray-50 text-gray-600">
        <tr>
          <th class="px-4 py-3 text-left">會員</th>
          <th class="px-4 py-3 text-left">Email</th>
          <th class="px-4 py-3 text-left">手機</th>
          <th class="px-4 py-3 text-center">角色</th>
          <th class="px-4 py-3 text-center">狀態</th>
          <th class="px-4 py-3 text-left">加入時間</th>
          <th class="px-4 py-3"></th>
        </tr>
      </thead>
      <tbody class="divide-y">
        <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50">
          <td class="px-4 py-3">
            <div class="flex items-center gap-2">
              <img v-if="user.avatar" :src="user.avatar" :alt="user.name"
                class="w-8 h-8 rounded-full" />
              <div v-else class="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-xs">
                {{ user.name?.[0] }}
              </div>
              {{ user.name }}
            </div>
          </td>
          <td class="px-4 py-3 text-gray-500">{{ user.email || '-' }}</td>
          <td class="px-4 py-3 text-gray-500">{{ user.phone || '-' }}</td>
          <td class="px-4 py-3 text-center">
            <span :class="user.role === 'admin' ? 'bg-purple-100 text-purple-700' : 'bg-gray-100 text-gray-500'"
              class="text-xs px-2 py-1 rounded-full">
              {{ user.role === 'admin' ? '管理員' : '一般' }}
            </span>
          </td>
          <td class="px-4 py-3 text-center">
            <span :class="user.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'"
              class="text-xs px-2 py-1 rounded-full">
              {{ user.is_active ? '正常' : '停用' }}
            </span>
          </td>
          <td class="px-4 py-3 text-gray-400 text-xs">{{ new Date(user.created_at).toLocaleDateString('zh-TW') }}</td>
          <td class="px-4 py-3 text-right">
            <button @click="toggleActive(user.id)"
              :class="user.is_active ? 'text-red-500 hover:underline' : 'text-green-600 hover:underline'"
              class="text-xs">
              {{ user.is_active ? '停用' : '啟用' }}
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'

const users = ref<any[]>([])

async function fetch() {
  const { data } = await api.get('/api/v1/users?page_size=100')
  users.value = data.items
}

async function toggleActive(id: number) {
  await api.patch(`/api/v1/users/${id}/toggle-active`)
  await fetch()
}

onMounted(fetch)
</script>
