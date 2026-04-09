<template>
  <div>
    <!-- Hero Banner -->
    <section class="bg-gradient-to-r from-primary-600 to-primary-400 text-white py-20">
      <div class="max-w-7xl mx-auto px-4 text-center">
        <h1 class="text-4xl font-bold mb-4">歡迎來到電商商城</h1>
        <p class="text-lg opacity-90 mb-8">精選商品，快速到貨</p>
        <router-link to="/products"
          class="bg-white text-primary-600 font-semibold px-8 py-3 rounded-xl hover:bg-gray-50 transition-colors">
          立即購物
        </router-link>
      </div>
    </section>

    <!-- Featured Products -->
    <section class="max-w-7xl mx-auto px-4 py-12">
      <h2 class="text-2xl font-bold mb-6">精選商品</h2>
      <div v-if="loading" class="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div v-for="i in 8" :key="i" class="bg-gray-200 rounded-xl h-64 animate-pulse"></div>
      </div>
      <div v-else class="grid grid-cols-2 md:grid-cols-4 gap-6">
        <ProductCard v-for="product in products" :key="product.id" :product="product" />
      </div>
      <div class="text-center mt-8">
        <router-link to="/products" class="text-primary-600 hover:underline font-medium">
          查看全部商品 →
        </router-link>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'
import type { Product } from '@/types'
import ProductCard from '@/components/ui/ProductCard.vue'

const products = ref<Product[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await api.get('/api/v1/products?page_size=8')
    products.value = data.items
  } finally {
    loading.value = false
  }
})
</script>
