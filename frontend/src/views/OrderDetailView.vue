<template>
  <div class="max-w-3xl mx-auto px-4 py-8">
    <div v-if="order">
      <div class="flex items-center gap-3 mb-6">
        <router-link to="/orders" class="text-gray-400 hover:text-gray-600">← 回訂單列表</router-link>
      </div>
      <div class="bg-white rounded-xl shadow-sm p-6">
        <div class="flex justify-between items-start mb-6">
          <div>
            <h1 class="text-xl font-bold">訂單 {{ order.order_no }}</h1>
            <p class="text-gray-400 text-sm mt-1">{{ new Date(order.created_at).toLocaleString('zh-TW') }}</p>
          </div>
          <span :class="statusClass(order.status)" class="text-sm px-3 py-1 rounded-full">
            {{ statusText(order.status) }}
          </span>
        </div>

        <!-- Items -->
        <div class="border-t pt-4">
          <h2 class="font-semibold mb-3">商品明細</h2>
          <div v-for="item in order.items" :key="item.id" class="flex justify-between py-2 text-sm">
            <span>{{ item.product_name }}<span v-if="item.variant_name"> ({{ item.variant_name }})</span> × {{ item.quantity }}</span>
            <span>NT$ {{ (item.unit_price * item.quantity).toLocaleString() }}</span>
          </div>
        </div>

        <!-- Summary -->
        <div class="border-t mt-4 pt-4 space-y-1 text-sm">
          <div v-if="order.discount_amount > 0" class="flex justify-between text-green-600">
            <span>折扣</span>
            <span>- NT$ {{ order.discount_amount.toLocaleString() }}</span>
          </div>
          <div class="flex justify-between font-bold text-lg">
            <span>合計</span>
            <span class="text-primary-600">NT$ {{ order.total.toLocaleString() }}</span>
          </div>
        </div>

        <!-- Delivery Info -->
        <div class="border-t mt-4 pt-4 text-sm space-y-1 text-gray-600">
          <p><span class="font-medium">配送方式：</span>{{ order.logistics_type === 'home' ? '宅配' : '超商取貨' }}</p>
          <p v-if="order.tracking_no"><span class="font-medium">物流單號：</span>{{ order.tracking_no }}</p>
          <p v-if="order.cvs_store_name"><span class="font-medium">取貨門市：</span>{{ order.cvs_store_name }}</p>
        </div>
      </div>
    </div>
    <div v-else-if="loading" class="flex justify-center py-20">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'
import type { Order } from '@/types'

const route = useRoute()
const order = ref<Order | null>(null)
const loading = ref(true)

function statusText(status: string) {
  const map: Record<string, string> = {
    pending_payment: '待付款', paid: '已付款', processing: '處理中',
    shipped: '運送中', delivered: '已送達', cancelled: '已取消',
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
    const { data } = await api.get(`/api/v1/orders/my/${route.params.id}`)
    order.value = data
  } finally {
    loading.value = false
  }
})
</script>
