<template>
  <div>
    <div class="flex gap-2 mb-4">
      <button v-for="s in statusFilters" :key="s.value" @click="statusFilter = s.value; fetch()"
        :class="['px-3 py-1.5 rounded-lg text-sm', statusFilter === s.value ? 'bg-blue-600 text-white' : 'bg-white border text-gray-600 hover:bg-gray-50']">
        {{ s.label }}
      </button>
    </div>

    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50 text-gray-600">
          <tr>
            <th class="px-4 py-3 text-left">訂單編號</th>
            <th class="px-4 py-3 text-left">下單時間</th>
            <th class="px-4 py-3 text-right">金額</th>
            <th class="px-4 py-3 text-center">付款</th>
            <th class="px-4 py-3 text-center">物流</th>
            <th class="px-4 py-3 text-center">狀態</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y">
          <tr v-for="order in orders" :key="order.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-mono text-xs">{{ order.order_no }}</td>
            <td class="px-4 py-3 text-gray-500">{{ formatDate(order.created_at) }}</td>
            <td class="px-4 py-3 text-right font-medium">NT$ {{ order.total.toLocaleString() }}</td>
            <td class="px-4 py-3 text-center">
              <span :class="order.payment_status === 'paid' ? 'bg-green-100 text-green-700' : 'bg-yellow-100 text-yellow-700'"
                class="text-xs px-2 py-1 rounded-full">
                {{ order.payment_status === 'paid' ? '已付款' : '待付款' }}
              </span>
            </td>
            <td class="px-4 py-3 text-center text-xs text-gray-500">
              {{ order.logistics_type === 'home' ? '宅配' : '超商' }}
            </td>
            <td class="px-4 py-3 text-center">
              <select @change="updateStatus(order.id, $event)"
                :value="order.status"
                class="text-xs border rounded px-2 py-1 focus:outline-none">
                <option value="pending_payment">待付款</option>
                <option value="paid">已付款</option>
                <option value="processing">處理中</option>
                <option value="shipped">運送中</option>
                <option value="delivered">已送達</option>
                <option value="cancelled">已取消</option>
              </select>
            </td>
            <td class="px-4 py-3 text-right">
              <router-link :to="`/orders/${order.id}`" class="text-blue-600 hover:underline text-xs">
                詳情
              </router-link>
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
const statusFilter = ref('')

const statusFilters = [
  { value: '', label: '全部' },
  { value: 'paid', label: '待出貨' },
  { value: 'shipped', label: '運送中' },
  { value: 'delivered', label: '已送達' },
]

function formatDate(d: string) {
  return new Date(d).toLocaleString('zh-TW', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
}

async function fetch() {
  const params = new URLSearchParams({ page: '1', page_size: '50' })
  if (statusFilter.value) params.set('status', statusFilter.value)
  const { data } = await api.get(`/api/v1/orders?${params}`)
  orders.value = data.items
}

async function updateStatus(orderId: number, e: Event) {
  const status = (e.target as HTMLSelectElement).value
  await api.patch(`/api/v1/orders/${orderId}/status?new_status=${status}`)
}

onMounted(fetch)
</script>
