<template>
  <div v-if="product" class="max-w-5xl mx-auto px-4 py-8">
    <div class="grid md:grid-cols-2 gap-8">
      <!-- Images -->
      <div>
        <div class="aspect-square bg-gray-100 rounded-xl overflow-hidden mb-3">
          <img v-if="product.images[selectedImage]" :src="product.images[selectedImage]"
            :alt="product.name" class="w-full h-full object-cover" />
          <div v-else class="w-full h-full flex items-center justify-center text-gray-300">
            <svg class="w-24 h-24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
        <div v-if="product.images.length > 1" class="flex gap-2">
          <button v-for="(img, i) in product.images" :key="i" @click="selectedImage = i"
            :class="['w-16 h-16 rounded-lg overflow-hidden border-2', selectedImage === i ? 'border-primary-500' : 'border-transparent']">
            <img :src="img" :alt="`${product.name} ${i+1}`" class="w-full h-full object-cover" />
          </button>
        </div>
      </div>

      <!-- Product Info -->
      <div>
        <h1 class="text-2xl font-bold text-gray-900 mb-2">{{ product.name }}</h1>
        <p class="text-3xl font-bold text-primary-600 mb-4">NT$ {{ displayPrice.toLocaleString() }}</p>

        <!-- Variants -->
        <div v-if="product.has_variants && product.variants.length > 0" class="mb-4">
          <p class="text-sm font-medium text-gray-700 mb-2">規格</p>
          <div class="flex flex-wrap gap-2">
            <button v-for="variant in product.variants" :key="variant.id"
              @click="selectedVariant = variant"
              :disabled="variant.stock === 0"
              :class="['px-4 py-2 rounded-lg border text-sm transition-colors',
                selectedVariant?.id === variant.id ? 'border-primary-500 bg-primary-50 text-primary-600' : 'border-gray-300 hover:border-primary-300',
                variant.stock === 0 ? 'opacity-40 cursor-not-allowed' : '']">
              {{ variant.name }}
              <span v-if="variant.stock === 0" class="ml-1 text-xs">(缺貨)</span>
            </button>
          </div>
        </div>

        <!-- Quantity -->
        <div class="flex items-center gap-3 mb-6">
          <p class="text-sm font-medium text-gray-700">數量</p>
          <div class="flex items-center border rounded-lg">
            <button @click="qty = Math.max(1, qty - 1)" class="px-3 py-2 hover:bg-gray-100">−</button>
            <span class="px-4 py-2 min-w-[3rem] text-center">{{ qty }}</span>
            <button @click="qty++" class="px-3 py-2 hover:bg-gray-100">+</button>
          </div>
        </div>

        <!-- Add to Cart -->
        <button @click="addToCart"
          :disabled="addingToCart || product.status === 'out_of_stock'"
          class="w-full bg-primary-500 hover:bg-primary-600 text-white font-semibold py-3 px-6 rounded-xl transition-colors disabled:opacity-50">
          {{ addingToCart ? '加入中...' : '加入購物車' }}
        </button>

        <!-- Description -->
        <div v-if="product.description" class="mt-8">
          <h2 class="font-semibold text-gray-700 mb-2">商品說明</h2>
          <p class="text-gray-600 whitespace-pre-line">{{ product.description }}</p>
        </div>
      </div>
    </div>
  </div>
  <div v-else-if="loading" class="flex justify-center py-20">
    <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api'
import type { Product, ProductVariant } from '@/types'
import { useCartStore } from '@/stores/cart'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const cartStore = useCartStore()
const authStore = useAuthStore()

const product = ref<Product | null>(null)
const loading = ref(true)
const selectedImage = ref(0)
const selectedVariant = ref<ProductVariant | null>(null)
const qty = ref(1)
const addingToCart = ref(false)

const displayPrice = computed(() => selectedVariant.value?.price ?? product.value?.base_price ?? 0)

async function addToCart() {
  if (!authStore.isLoggedIn) {
    router.push({ name: 'login', query: { redirect: route.fullPath } })
    return
  }
  addingToCart.value = true
  try {
    await cartStore.addItem(product.value!.id, selectedVariant.value?.id ?? null, qty.value)
    alert('已加入購物車')
  } finally {
    addingToCart.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get(`/api/v1/products/${route.params.slug}`)
    product.value = data
    if (data.variants.length > 0) {
      selectedVariant.value = data.variants[0]
    }
  } finally {
    loading.value = false
  }
})
</script>
