<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">我的訂單</h1>

    <div v-if="loading" class="space-y-4">
      <div v-for="i in 3" :key="i" class="bg-gray-200 rounded-xl h-24 animate-pulse"></div>
    </div>
    <div v-else-if="orders.length === 0" class="text-center py-20 text-gray-400">
      還沒有訂單
    </div>
    <div v-else class="space-y-4">
      <router-link v-for="order in orders" :key="order.id" :to="`/orders/${order.id}`"
        class="block bg-white rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow">
        <div class="flex justify-between items-start">
          <div>
            <p class="font-medium">訂單 {{ order.order_no }}</p>
            <p class="text-sm text-gray-400 mt-1">{{ formatDate(order.created_at) }}</p>
          </div>
          <div class="text-right">
            <span :class="statusClass(order.status)" class="text-xs px-2 py-1 rounded-full">
              {{ statusText(order.status) }}
            </span>
            <p class="font-bold text-primary-600 mt-1">NT$ {{ order.total.toLocaleString() }}</p>
          </div>
        </div>
        <p class="text-sm text-gray-500 mt-2">共 {{ order.items.length }} 件商品</p>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'
import type { Order } from '@/types'

const orders = ref<Order[]>([])
const loading = ref(true)

function formatDate(d: string) {
  return new Date(d).toLocaleDateString('zh-TW')
}

function statusText(status: string) {
  const map: Record<string, string> = {
    pending_payment: '待付款', paid: '已付款', processing: '處理中',
    shipped: '運送中', delivered: '已送達', cancelled: '已取消', refunded: '已退款',
  }
  return map[status] || status
}

function statusClass(status: string) {
  const map: Record<string, string> = {
    pending_payment: 'bg-yellow-100 text-yellow-700',
    paid: 'bg-blue-100 text-blue-700',
    shipped: 'bg-purple-100 text-purple-700',
    delivered: 'bg-green-100 text-green-700',
    cancelled: 'bg-gray-100 text-gray-500',
  }
  return map[status] || 'bg-gray-100 text-gray-500'
}

onMounted(async () => {
  try {
    const { data } = await api.get('/api/v1/orders/my')
    orders.value = data.items
  } finally {
    loading.value = false
  }
})
</script>
