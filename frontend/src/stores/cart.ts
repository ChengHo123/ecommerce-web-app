import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'
import type { Cart } from '@/types'

export const useCartStore = defineStore('cart', () => {
  const cart = ref<Cart | null>(null)

  const itemCount = computed(() => cart.value?.items.reduce((sum, i) => sum + i.quantity, 0) ?? 0)
  const total = computed(() => cart.value?.total ?? 0)

  async function fetchCart() {
    try {
      const { data } = await api.get('/api/v1/cart')
      cart.value = data
    } catch {
      cart.value = null
    }
  }

  async function addItem(product_id: number, variant_id: number | null, quantity = 1) {
    await api.post('/api/v1/cart/items', { product_id, variant_id, quantity })
    await fetchCart()
  }

  async function updateItem(item_id: number, quantity: number) {
    await api.patch(`/api/v1/cart/items/${item_id}`, { quantity })
    await fetchCart()
  }

  async function removeItem(item_id: number) {
    await api.delete(`/api/v1/cart/items/${item_id}`)
    await fetchCart()
  }

  async function clearCart() {
    await api.delete('/api/v1/cart')
    cart.value = null
  }

  return { cart, itemCount, total, fetchCart, addItem, updateItem, removeItem, clearCart }
})
