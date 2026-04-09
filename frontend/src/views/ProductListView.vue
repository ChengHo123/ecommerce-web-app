<template>
  <div class="max-w-7xl mx-auto px-4 py-8">
    <div class="flex gap-8">
      <!-- Sidebar: Categories -->
      <aside class="w-48 shrink-0 hidden md:block">
        <h2 class="font-semibold text-gray-700 mb-3">商品分類</h2>
        <ul class="space-y-1">
          <li>
            <button @click="selectedCategory = null"
              :class="['w-full text-left px-3 py-2 rounded-lg text-sm', !selectedCategory ? 'bg-primary-50 text-primary-600' : 'text-gray-600 hover:bg-gray-100']">
              全部商品
            </button>
          </li>
          <li v-for="cat in categories" :key="cat.id">
            <button @click="selectedCategory = cat.id"
              :class="['w-full text-left px-3 py-2 rounded-lg text-sm', selectedCategory === cat.id ? 'bg-primary-50 text-primary-600' : 'text-gray-600 hover:bg-gray-100']">
              {{ cat.name }}
            </button>
          </li>
        </ul>
      </aside>

      <!-- Main Content -->
      <div class="flex-1">
        <!-- Search -->
        <div class="flex gap-3 mb-6">
          <input v-model="search" @keyup.enter="fetchProducts"
            type="text" placeholder="搜尋商品..."
            class="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-primary-400" />
          <button @click="fetchProducts" class="bg-primary-500 text-white px-6 py-2 rounded-lg hover:bg-primary-600">
            搜尋
          </button>
        </div>

        <!-- Products Grid -->
        <div v-if="loading" class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          <div v-for="i in 12" :key="i" class="bg-gray-200 rounded-xl h-64 animate-pulse"></div>
        </div>
        <div v-else-if="products.length === 0" class="text-center py-20 text-gray-400">
          找不到商品
        </div>
        <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          <ProductCard v-for="product in products" :key="product.id" :product="product" />
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-8">
          <button v-for="p in totalPages" :key="p" @click="currentPage = p; fetchProducts()"
            :class="['px-4 py-2 rounded-lg text-sm', currentPage === p ? 'bg-primary-500 text-white' : 'bg-white border hover:bg-gray-50']">
            {{ p }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import api from '@/api'
import type { Product, Category } from '@/types'
import ProductCard from '@/components/ui/ProductCard.vue'

const products = ref<Product[]>([])
const categories = ref<Category[]>([])
const loading = ref(false)
const search = ref('')
const selectedCategory = ref<number | null>(null)
const currentPage = ref(1)
const totalPages = ref(1)

async function fetchProducts() {
  loading.value = true
  try {
    const params = new URLSearchParams({ page: String(currentPage.value), page_size: '20' })
    if (search.value) params.set('search', search.value)
    if (selectedCategory.value) params.set('category_id', String(selectedCategory.value))
    const { data } = await api.get(`/api/v1/products?${params}`)
    products.value = data.items
    totalPages.value = data.total_pages
  } finally {
    loading.value = false
  }
}

watch(selectedCategory, () => { currentPage.value = 1; fetchProducts() })

onMounted(async () => {
  const [catData] = await Promise.all([
    api.get('/api/v1/categories').then(r => r.data),
    fetchProducts(),
  ])
  categories.value = catData
})
</script>
