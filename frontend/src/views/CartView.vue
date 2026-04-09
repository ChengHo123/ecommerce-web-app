<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">購物車</h1>

    <div v-if="cartStore.cart && cartStore.cart.items.length > 0" class="grid md:grid-cols-3 gap-8">
      <!-- Cart Items -->
      <div class="md:col-span-2 space-y-4">
        <div v-for="item in cartStore.cart.items" :key="item.id"
          class="bg-white rounded-xl p-4 flex gap-4 shadow-sm">
          <div class="w-20 h-20 bg-gray-100 rounded-lg overflow-hidden shrink-0">
            <img v-if="item.product_image" :src="item.product_image" :alt="item.product_name"
              class="w-full h-full object-cover" />
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-medium truncate">{{ item.product_name }}</p>
            <p v-if="item.variant_id" class="text-sm text-gray-500">規格: {{ item.variant_id }}</p>
            <p class="text-primary-600 font-bold mt-1">NT$ {{ item.unit_price.toLocaleString() }}</p>
          </div>
          <div class="flex flex-col items-end gap-2">
            <button @click="cartStore.removeItem(item.id)" class="text-gray-400 hover:text-red-500">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            <div class="flex items-center border rounded-lg text-sm">
              <button @click="cartStore.updateItem(item.id, item.quantity - 1)"
                :disabled="item.quantity <= 1" class="px-2 py-1 hover:bg-gray-100 disabled:opacity-40">−</button>
              <span class="px-3">{{ item.quantity }}</span>
              <button @click="cartStore.updateItem(item.id, item.quantity + 1)"
                class="px-2 py-1 hover:bg-gray-100">+</button>
            </div>
            <p class="font-semibold">NT$ {{ item.subtotal.toLocaleString() }}</p>
          </div>
        </div>
      </div>

      <!-- Order Summary -->
      <div class="bg-white rounded-xl p-6 shadow-sm h-fit">
        <h2 class="font-semibold text-lg mb-4">訂單摘要</h2>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-500">商品小計</span>
            <span>NT$ {{ cartStore.total.toLocaleString() }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-500">運費</span>
            <span>計算於結帳時</span>
          </div>
        </div>
        <div class="border-t my-4"></div>
        <div class="flex justify-between font-bold text-lg">
          <span>合計</span>
          <span class="text-primary-600">NT$ {{ cartStore.total.toLocaleString() }}</span>
        </div>
        <router-link to="/checkout"
          class="block mt-4 bg-primary-500 hover:bg-primary-600 text-white text-center font-semibold py-3 rounded-xl transition-colors">
          前往結帳
        </router-link>
      </div>
    </div>

    <div v-else class="text-center py-20">
      <svg class="w-20 h-20 text-gray-200 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
          d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
      <p class="text-gray-400 mb-4">購物車是空的</p>
      <router-link to="/products" class="text-primary-600 hover:underline">去購物 →</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'

const cartStore = useCartStore()
const authStore = useAuthStore()

onMounted(() => {
  if (authStore.isLoggedIn) {
    cartStore.fetchCart()
  }
})
</script>
