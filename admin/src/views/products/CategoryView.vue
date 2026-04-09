<template>
  <div class="grid grid-cols-2 gap-6">
    <!-- Category List -->
    <div class="bg-white rounded-xl shadow-sm p-6">
      <h2 class="font-semibold mb-4">分類列表</h2>
      <div v-for="cat in categories" :key="cat.id"
        class="flex justify-between items-center py-2 border-b last:border-0">
        <span>{{ cat.name }}</span>
        <div class="flex gap-2">
          <button @click="editCategory(cat)" class="text-blue-600 hover:underline text-sm">編輯</button>
          <button @click="deleteCategory(cat.id)" class="text-red-500 hover:underline text-sm">刪除</button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Form -->
    <div class="bg-white rounded-xl shadow-sm p-6">
      <h2 class="font-semibold mb-4">{{ editingId ? '編輯分類' : '新增分類' }}</h2>
      <div class="space-y-3">
        <div>
          <label class="text-sm text-gray-600 block mb-1">分類名稱</label>
          <input v-model="form.name" type="text" class="w-full border rounded-lg px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="text-sm text-gray-600 block mb-1">Slug</label>
          <input v-model="form.slug" type="text" class="w-full border rounded-lg px-3 py-2 text-sm" />
        </div>
        <div>
          <label class="text-sm text-gray-600 block mb-1">父分類</label>
          <select v-model="form.parent_id" class="w-full border rounded-lg px-3 py-2 text-sm">
            <option :value="null">無</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>
        <div class="flex gap-2">
          <button @click="save"
            class="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium px-4 py-2 rounded-lg">
            {{ editingId ? '更新' : '新增' }}
          </button>
          <button v-if="editingId" @click="resetForm" class="border px-4 py-2 rounded-lg text-sm text-gray-600">
            取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import api from '@/api'

const categories = ref<any[]>([])
const editingId = ref<number | null>(null)
const form = reactive({ name: '', slug: '', parent_id: null as number | null })

async function fetchCategories() {
  const { data } = await api.get('/api/v1/categories')
  categories.value = data
}

function editCategory(cat: any) {
  editingId.value = cat.id
  form.name = cat.name
  form.slug = cat.slug
  form.parent_id = cat.parent_id
}

function resetForm() {
  editingId.value = null
  form.name = ''
  form.slug = ''
  form.parent_id = null
}

async function save() {
  if (editingId.value) {
    await api.patch(`/api/v1/categories/${editingId.value}`, form)
  } else {
    await api.post('/api/v1/categories', form)
  }
  resetForm()
  await fetchCategories()
}

async function deleteCategory(id: number) {
  if (!confirm('確定刪除？')) return
  await api.delete(`/api/v1/categories/${id}`)
  await fetchCategories()
}

onMounted(fetchCategories)
</script>
