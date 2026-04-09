<template>
  <div class="max-w-3xl">
    <div class="bg-white rounded-xl shadow-sm p-6">
      <h2 class="text-lg font-semibold mb-6">{{ isEdit ? '編輯商品' : '新增商品' }}</h2>

      <div class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="text-sm font-medium text-gray-600 block mb-1">商品名稱</label>
            <input v-model="form.name" type="text" class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </div>
          <div>
            <label class="text-sm font-medium text-gray-600 block mb-1">網址 Slug</label>
            <input v-model="form.slug" type="text" class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </div>
        </div>

        <div>
          <label class="text-sm font-medium text-gray-600 block mb-1">商品描述</label>
          <textarea v-model="form.description" rows="4" class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"></textarea>
        </div>

        <div class="grid grid-cols-3 gap-4">
          <div>
            <label class="text-sm font-medium text-gray-600 block mb-1">定價 (NT$)</label>
            <input v-model.number="form.base_price" type="number" class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </div>
          <div>
            <label class="text-sm font-medium text-gray-600 block mb-1">庫存</label>
            <input v-model.number="form.stock" type="number" class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400" />
          </div>
          <div>
            <label class="text-sm font-medium text-gray-600 block mb-1">狀態</label>
            <select v-model="form.status" class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400">
              <option value="active">上架</option>
              <option value="inactive">下架</option>
              <option value="out_of_stock">缺貨</option>
            </select>
          </div>
        </div>

        <div>
          <label class="text-sm font-medium text-gray-600 block mb-1">分類</label>
          <select v-model="form.category_id" class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400">
            <option :value="null">無分類</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>

        <!-- Variants -->
        <div>
          <div class="flex items-center justify-between mb-2">
            <label class="text-sm font-medium text-gray-600">商品規格 (變體)</label>
            <button @click="addVariant" class="text-blue-600 hover:underline text-sm">+ 新增規格</button>
          </div>
          <div v-for="(v, i) in form.variants" :key="i" class="flex gap-3 mb-2">
            <input v-model="v.name" placeholder="規格名稱 (e.g. 紅色/M)" class="flex-1 border rounded-lg px-3 py-2 text-sm" />
            <input v-model.number="v.price" type="number" placeholder="價格" class="w-28 border rounded-lg px-3 py-2 text-sm" />
            <input v-model.number="v.stock" type="number" placeholder="庫存" class="w-24 border rounded-lg px-3 py-2 text-sm" />
            <button @click="form.variants.splice(i, 1)" class="text-red-400 hover:text-red-600">✕</button>
          </div>
        </div>
      </div>

      <div class="flex gap-3 mt-6">
        <button @click="save" :disabled="saving"
          class="bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-2 rounded-lg disabled:opacity-50">
          {{ saving ? '儲存中...' : '儲存' }}
        </button>
        <router-link to="/products" class="border px-6 py-2 rounded-lg text-gray-600 hover:bg-gray-50">取消</router-link>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const isEdit = computed(() => !!route.params.id)
const saving = ref(false)
const categories = ref<any[]>([])

const form = reactive({
  name: '',
  slug: '',
  description: '',
  base_price: 0,
  stock: 0,
  status: 'active',
  category_id: null as number | null,
  images: [] as string[],
  has_variants: false,
  variants: [] as any[],
})

function addVariant() {
  form.has_variants = true
  form.variants.push({ name: '', price: form.base_price, stock: 0 })
}

async function save() {
  saving.value = true
  try {
    if (isEdit.value) {
      await api.patch(`/api/v1/products/${route.params.id}`, form)
    } else {
      await api.post('/api/v1/products', form)
    }
    router.push('/products')
  } catch (e: any) {
    alert(e.response?.data?.detail || '儲存失敗')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  const { data: cats } = await api.get('/api/v1/categories')
  categories.value = cats

  if (isEdit.value) {
    const { data } = await api.get(`/api/v1/products/${route.params.id}`)
    Object.assign(form, data)
  }
})
</script>
