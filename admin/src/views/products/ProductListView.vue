<template>
  <div>
    <div class="flex justify-between items-center mb-4">
      <input v-model="search" placeholder="搜尋商品..." @keyup.enter="fetch"
        class="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400 w-64" />
      <router-link to="/products/new"
        class="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
        + 新增商品
      </router-link>
    </div>

    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-600">
          <tr>
            <th class="px-4 py-3 text-left">商品名稱</th>
            <th class="px-4 py-3 text-left">分類</th>
            <th class="px-4 py-3 text-right">價格</th>
            <th class="px-4 py-3 text-right">庫存</th>
            <th class="px-4 py-3 text-center">狀態</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y">
          <tr v-for="product in products" :key="product.id" class="hover:bg-gray-50">
            <td class="px-4 py-3">
              <div class="flex items-center gap-3">
                <img v-if="product.images[0]" :src="product.images[0]" :alt="product.name"
                  class="w-10 h-10 rounded-lg object-cover" />
                <div class="w-10 h-10 bg-gray-100 rounded-lg" v-else></div>
                <span class="font-medium">{{ product.name }}</span>
              </div>
            </td>
            <td class="px-4 py-3 text-gray-500">-</td>
            <td class="px-4 py-3 text-right">NT$ {{ product.base_price.toLocaleString() }}</td>
            <td class="px-4 py-3 text-right" :class="product.stock < 10 ? 'text-red-500 font-medium' : ''">
              {{ product.stock }}
            </td>
            <td class="px-4 py-3 text-center">
              <span :class="product.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'"
                class="px-2 py-1 rounded-full text-xs">
                {{ product.status === 'active' ? '上架' : '下架' }}
              </span>
            </td>
            <td class="px-4 py-3 text-right">
              <div class="flex justify-end gap-2">
                <router-link :to="`/products/${product.id}/edit`"
                  class="text-blue-600 hover:underline text-xs">編輯</router-link>
                <button @click="deleteProduct(product.id)" class="text-red-500 hover:underline text-xs">刪除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="flex justify-center gap-2 mt-4">
      <button v-for="p in totalPages" :key="p" @click="currentPage = p; fetch()"
        :class="['px-3 py-1 rounded text-sm', currentPage === p ? 'bg-blue-600 text-white' : 'bg-white border hover:bg-gray-50']">
        {{ p }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'

const products = ref<any[]>([])
const search = ref('')
const currentPage = ref(1)
const totalPages = ref(1)

async function fetch() {
  const params = new URLSearchParams({ page: String(currentPage.value), page_size: '20' })
  if (search.value) params.set('search', search.value)
  const { data } = await api.get(`/api/v1/products?${params}`)
  products.value = data.items
  totalPages.value = data.total_pages
}

async function deleteProduct(id: number) {
  if (!confirm('確定要刪除這個商品嗎？')) return
  await api.delete(`/api/v1/products/${id}`)
  await fetch()
}

onMounted(fetch)
</script>
