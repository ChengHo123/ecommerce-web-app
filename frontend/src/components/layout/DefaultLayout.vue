<template>
  <div class="min-h-screen flex flex-col">
    <header class="bg-white shadow-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <!-- Logo -->
        <router-link to="/" class="text-xl font-bold text-primary-600">電商商城</router-link>

        <!-- Navigation -->
        <nav class="hidden md:flex items-center gap-6">
          <router-link to="/products" class="text-gray-600 hover:text-primary-600">商品</router-link>
        </nav>

        <!-- Actions -->
        <div class="flex items-center gap-4">
          <!-- Cart -->
          <router-link to="/cart" class="relative p-2">
            <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <span v-if="cartStore.itemCount > 0"
              class="absolute -top-1 -right-1 bg-primary-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
              {{ cartStore.itemCount }}
            </span>
          </router-link>

          <!-- User -->
          <div v-if="authStore.isLoggedIn" class="flex items-center gap-2">
            <router-link to="/orders" class="text-gray-600 hover:text-primary-600 text-sm">訂單</router-link>
            <button @click="authStore.logout()" class="text-gray-600 hover:text-red-500 text-sm">登出</button>
          </div>
          <router-link v-else to="/login"
            class="bg-primary-500 text-white px-4 py-2 rounded-lg text-sm hover:bg-primary-600">
            登入
          </router-link>
        </div>
      </div>
    </header>

    <main class="flex-1">
      <router-view />
    </main>

    <footer class="bg-gray-800 text-gray-300 py-8 mt-12">
      <div class="max-w-7xl mx-auto px-4 text-center text-sm">
        © 2024 電商商城. All rights reserved.
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useCartStore } from '@/stores/cart'

const authStore = useAuthStore()
const cartStore = useCartStore()

onMounted(async () => {
  await authStore.fetchUser()
  if (authStore.isLoggedIn) {
    await cartStore.fetchCart()
  }
})
</script>
