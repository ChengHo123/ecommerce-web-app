<template>
  <div>
    <h2 class="text-lg font-semibold mb-4">待出貨訂單</h2>
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-600">
          <tr>
            <th class="px-4 py-3 text-left">訂單編號</th>
            <th class="px-4 py-3 text-left">配送方式</th>
            <th class="px-4 py-3 text-left">收件資訊</th>
            <th class="px-4 py-3 text-center">物流狀態</th>
            <th class="px-4 py-3 text-left">物流單號</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y">
          <tr v-for="order in orders" :key="order.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-mono text-xs">{{ order.order_no }}</td>
            <td class="px-4 py-3">{{ order.logistics_type === 'home' ? '🏠 宅配' : '🏪 超商' }}</td>
            <td class="px-4 py-3 text-gray-500 text-xs">
              <template v-if="order.logistics_type === 'cvs'">
                {{ order.cvs_store_name }} ({{ order.cvs_store_id }})
              </template>
              <template v-else-if="order.shipping_address">
                {{ order.shipping_address.recipient_name }} {{ order.shipping_address.phone }}
              </template>
            </td>
            <td class="px-4 py-3 text-center">
              <span class="text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-700">
                {{ logisticsStatusText(order.logistics_status) }}
              </span>
            </td>
            <td class="px-4 py-3 font-mono text-xs text-gray-500">
              {{ order.tracking_no || '-' }}
            </td>
            <td class="px-4 py-3 text-right">
              <button
                v-if="order.logistics_status === 'pending'"
                @click="createShipment(order.id)"
                :disabled="creating === order.id"
                class="bg-green-600 hover:bg-green-700 text-white text-xs font-medium px-3 py-1.5 rounded-lg disabled:opacity-50">
                {{ creating === order.id ? '建立中...' : '建立物流單' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'

const orders = ref<any[]>([])
const creating = ref<number | null>(null)

function logisticsStatusText(s: string) {
  const map: Record<string, string> = {
    pending: '待出貨', created: '已建單', in_transit: '運送中',
    arrived: '已到門市', delivered: '已取貨', failed: '配送失敗',
  }
  return map[s] || s
}

async function fetchOrders() {
  const { data } = await api.get('/api/v1/orders?status=paid&page_size=100')
  orders.value = data.items
}

async function createShipment(orderId: number) {
  creating.value = orderId
  try {
    await api.post(`/api/v1/logistics/create-shipment/${orderId}`)
    await fetchOrders()
  } catch (e: any) {
    alert(e.response?.data?.detail || '建立失敗')
  } finally {
    creating.value = null
  }
}

onMounted(fetchOrders)
</script>
