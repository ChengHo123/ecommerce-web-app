<template>
  <div v-if="order" class="max-w-3xl">
    <div class="bg-white rounded-xl shadow-sm p-6">
      <div class="flex justify-between items-start mb-6">
        <div>
          <h2 class="text-lg font-semibold">訂單 {{ order.order_no }}</h2>
          <p class="text-gray-400 text-sm">{{ new Date(order.created_at).toLocaleString('zh-TW') }}</p>
        </div>
        <select @change="updateStatus($event)" :value="order.status"
          class="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400">
          <option value="pending_payment">待付款</option>
          <option value="paid">已付款</option>
          <option value="processing">處理中</option>
          <option value="shipped">運送中</option>
          <option value="delivered">已送達</option>
          <option value="cancelled">已取消</option>
        </select>
      </div>

      <!-- Items -->
      <div class="border rounded-lg overflow-hidden mb-4">
        <table class="w-full text-sm">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-4 py-2 text-left">商品</th>
              <th class="px-4 py-2 text-right">單價</th>
              <th class="px-4 py-2 text-center">數量</th>
              <th class="px-4 py-2 text-right">小計</th>
            </tr>
          </thead>
          <tbody class="divide-y">
            <tr v-for="item in order.items" :key="item.id">
              <td class="px-4 py-2">
                {{ item.product_name }}
                <span v-if="item.variant_name" class="text-gray-400">({{ item.variant_name }})</span>
              </td>
              <td class="px-4 py-2 text-right">NT$ {{ item.unit_price.toLocaleString() }}</td>
              <td class="px-4 py-2 text-center">{{ item.quantity }}</td>
              <td class="px-4 py-2 text-right">NT$ {{ (item.unit_price * item.quantity).toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="flex justify-between font-bold text-lg mb-6">
        <span>合計</span>
        <span>NT$ {{ order.total.toLocaleString() }}</span>
      </div>

      <!-- Delivery Info -->
      <div class="grid grid-cols-2 gap-4 text-sm">
        <div>
          <p class="font-medium mb-1">配送資訊</p>
          <p class="text-gray-600">方式：{{ order.logistics_type === 'home' ? '宅配' : '超商取貨' }}</p>
          <p v-if="order.tracking_no" class="text-gray-600">物流單號：{{ order.tracking_no }}</p>
          <p v-if="order.cvs_store_name" class="text-gray-600">取貨門市：{{ order.cvs_store_name }}</p>
        </div>
        <div v-if="order.shipping_address">
          <p class="font-medium mb-1">收件地址</p>
          <p class="text-gray-600">{{ order.shipping_address.recipient_name }}</p>
          <p class="text-gray-600">{{ order.shipping_address.phone }}</p>
          <p class="text-gray-600">{{ order.shipping_address.city }}{{ order.shipping_address.district }}{{ order.shipping_address.address }}</p>
        </div>
      </div>

      <!-- Create Shipment -->
      <div class="mt-6 pt-4 border-t" v-if="order.payment_status === 'paid' && order.logistics_status === 'pending'">
        <button @click="createShipment" :disabled="creating"
          class="bg-green-600 hover:bg-green-700 text-white font-medium px-4 py-2 rounded-lg disabled:opacity-50 text-sm">
          {{ creating ? '建立中...' : '建立物流單' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const order = ref<any>(null)
const creating = ref(false)

async function fetchOrder() {
  const { data } = await api.get(`/api/v1/orders/${route.params.id}`)
  order.value = data
}

async function updateStatus(e: Event) {
  const status = (e.target as HTMLSelectElement).value
  await api.patch(`/api/v1/orders/${order.value.id}/status?new_status=${status}`)
  await fetchOrder()
}

async function createShipment() {
  creating.value = true
  try {
    await api.post(`/api/v1/logistics/create-shipment/${order.value.id}`)
    await fetchOrder()
    alert('物流單已建立')
  } catch (e: any) {
    alert(e.response?.data?.detail || '建立失敗')
  } finally {
    creating.value = false
  }
}

onMounted(fetchOrder)
</script>
