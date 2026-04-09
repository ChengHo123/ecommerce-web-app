<template>
  <router-link :to="`/products/${product.slug}`" class="group">
    <div class="bg-white rounded-xl overflow-hidden shadow-sm hover:shadow-md transition-shadow">
      <div class="aspect-square bg-gray-100 overflow-hidden">
        <img
          v-if="product.images[0]"
          :src="product.images[0]"
          :alt="product.name"
          class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
        />
        <div v-else class="w-full h-full flex items-center justify-center text-gray-300">
          <svg class="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
      </div>
      <div class="p-4">
        <h3 class="font-medium text-gray-900 truncate">{{ product.name }}</h3>
        <p class="text-primary-600 font-bold mt-1">NT$ {{ product.base_price.toLocaleString() }}</p>
        <span v-if="product.status === 'out_of_stock'"
          class="inline-block mt-2 text-xs text-red-500 bg-red-50 px-2 py-1 rounded">
          缺貨中
        </span>
      </div>
    </div>
  </router-link>
</template>

<script setup lang="ts">
import type { Product } from '@/types'

defineProps<{ product: Product }>()
</script>
