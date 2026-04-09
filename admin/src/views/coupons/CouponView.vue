<template>
  <div class="grid grid-cols-2 gap-6">
    <!-- Coupon List -->
    <div class="bg-white rounded-xl shadow-sm p-6">
      <h2 class="font-semibold mb-4">折扣碼列表</h2>
      <div class="space-y-3">
        <div v-for="coupon in coupons" :key="coupon.id"
          class="flex justify-between items-center p-3 border rounded-lg">
          <div>
            <p class="font-mono font-semibold">{{ coupon.code }}</p>
            <p class="text-xs text-gray-400">
              {{ coupon.discount_type === 'percent' ? `${coupon.value}% 折扣` : `NT$ ${coupon.value} 折扣` }}
              · 已使用 {{ coupon.used_count }} 次
            </p>
          </div>
          <div class="flex items-center gap-2">
            <span :class="coupon.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-400'"
              class="text-xs px-2 py-1 rounded-full">
              {{ coupon.is_active ? '啟用' : '停用' }}
            </span>
            <button @click="deleteCoupon(coupon.id)" class="text-red-400 hover:text-red-600 text-xs">刪除</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Form -->
    <div class="bg-white rounded-xl shadow-sm p-6">
      <h2 class="font-semibold mb-4">新增折扣碼</h2>
      <div class="space-y-3">
        <div>
          <label class="text-sm text-gray-600 block mb-1">折扣碼</label>
          <input v-model="form.code" type="text" class="w-full border rounded-lg px-3 py-2 text-sm uppercase"
            placeholder="e.g. SAVE100" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-sm text-gray-600 block mb-1">折扣類型</label>
            <select v-model="form.discount_type" class="w-full border rounded-lg px-3 py-2 text-sm">
              <option value="fixed">固定金額 (NT$)</option>
              <option value="percent">百分比 (%)</option>
            </select>
          </div>
          <div>
            <label class="text-sm text-gray-600 block mb-1">折扣值</label>
            <input v-model.number="form.value" type="number" class="w-full border rounded-lg px-3 py-2 text-sm" />
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="text-sm text-gray-600 block mb-1">最低消費 (NT$)</label>
            <input v-model.number="form.min_amount" type="number" class="w-full border rounded-lg px-3 py-2 text-sm" />
          </div>
          <div>
            <label class="text-sm text-gray-600 block mb-1">使用次數上限</label>
            <input v-model.number="form.usage_limit" type="number" placeholder="不限" class="w-full border rounded-lg px-3 py-2 text-sm" />
          </div>
        </div>
        <div>
          <label class="text-sm text-gray-600 block mb-1">到期日</label>
          <input v-model="form.expires_at" type="datetime-local" class="w-full border rounded-lg px-3 py-2 text-sm" />
        </div>
        <button @click="save" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg text-sm">
          新增折扣碼
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import api from '@/api'

const coupons = ref<any[]>([])
const form = reactive({
  code: '',
  discount_type: 'fixed',
  value: 0,
  min_amount: 0,
  usage_limit: null as number | null,
  expires_at: '',
})

async function fetchCoupons() {
  const { data } = await api.get('/api/v1/coupons')
  coupons.value = data
}

async function save() {
  const payload: any = { ...form, code: form.code.toUpperCase() }
  if (!payload.usage_limit) payload.usage_limit = null
  if (!payload.expires_at) payload.expires_at = null
  await api.post('/api/v1/coupons', payload)
  Object.assign(form, { code: '', value: 0, min_amount: 0, usage_limit: null, expires_at: '' })
  await fetchCoupons()
}

async function deleteCoupon(id: number) {
  if (!confirm('確定刪除？')) return
  await api.delete(`/api/v1/coupons/${id}`)
  await fetchCoupons()
}

onMounted(fetchCoupons)
</script>
