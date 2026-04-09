<template>
  <div class="flex h-screen bg-gray-100">
    <!-- Sidebar -->
    <aside class="w-64 bg-gray-900 text-white flex flex-col">
      <div class="px-6 py-5 border-b border-gray-700">
        <h1 class="text-lg font-bold">電商後台</h1>
        <p class="text-gray-400 text-xs mt-1">{{ authStore.user?.name }}</p>
      </div>
      <nav class="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <router-link v-for="item in navItems" :key="item.to" :to="item.to"
          class="flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors"
          :class="$route.path.startsWith(item.to) ? 'bg-primary-500 text-white' : 'text-gray-300 hover:bg-gray-800'">
          <span>{{ item.icon }}</span>
          {{ item.label }}
        </router-link>
      </nav>
      <div class="px-3 py-4 border-t border-gray-700">
        <button @click="authStore.logout(); $router.push('/login')"
          class="w-full text-left px-3 py-2 text-gray-400 hover:text-white text-sm rounded-lg hover:bg-gray-800">
          登出
        </button>
      </div>
    </aside>

    <!-- Main -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <header class="bg-white shadow-sm px-6 py-4">
        <h2 class="text-lg font-semibold text-gray-800">{{ currentPageTitle }}</h2>
      </header>
      <main class="flex-1 overflow-y-auto p-6">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAdminAuthStore } from '@/stores/auth'

const authStore = useAdminAuthStore()
const route = useRoute()

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: '📊' },
  { to: '/products', label: '商品管理', icon: '📦' },
  { to: '/categories', label: '分類管理', icon: '🏷️' },
  { to: '/orders', label: '訂單管理', icon: '🛒' },
  { to: '/logistics', label: '物流管理', icon: '🚚' },
  { to: '/users', label: '會員管理', icon: '👥' },
  { to: '/coupons', label: '折扣碼', icon: '🎟️' },
]

const currentPageTitle = computed(() => {
  const item = navItems.find(n => route.path.startsWith(n.to))
  return item?.label || '後台管理'
})
</script>
