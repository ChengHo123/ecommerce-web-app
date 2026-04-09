<template>
  <div class="max-w-lg mx-auto px-4 py-16 text-center">
    <div v-if="loading" class="flex justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
    </div>

    <!-- Stripe Payment -->
    <div v-else-if="clientSecret" class="bg-white rounded-2xl shadow-lg p-8">
      <h1 class="text-xl font-bold mb-6">完成付款</h1>
      <div id="payment-element" class="mb-6"></div>
      <button @click="confirmStripePayment" :disabled="paying"
        class="w-full bg-primary-500 hover:bg-primary-600 text-white font-semibold py-3 rounded-xl disabled:opacity-50">
        {{ paying ? '付款中...' : '確認付款' }}
      </button>
    </div>

    <!-- LINE Pay success -->
    <div v-else class="bg-white rounded-2xl shadow-lg p-8">
      <div class="text-green-500 mb-4">
        <svg class="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <h1 class="text-xl font-bold mb-2">付款成功！</h1>
      <p class="text-gray-500 mb-6">您的訂單已成立</p>
      <router-link to="/orders" class="text-primary-600 hover:underline">查看訂單</router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { loadStripe } from '@stripe/stripe-js'
import api from '@/api'

const route = useRoute()
const router = useRouter()
const loading = ref(true)
const paying = ref(false)
const clientSecret = ref('')
let stripe: any = null
let elements: any = null

onMounted(async () => {
  const orderId = route.query.order_id
  if (!orderId) {
    loading.value = false
    return
  }

  try {
    const { data } = await api.post(`/api/v1/payment/stripe/create-intent?order_id=${orderId}`)
    clientSecret.value = data.client_secret

    stripe = await loadStripe(data.publishable_key)
    elements = stripe.elements({ clientSecret: data.client_secret })
    const paymentElement = elements.create('payment')

    setTimeout(() => {
      paymentElement.mount('#payment-element')
    }, 100)
  } catch {
    // may be LINE Pay redirect, just show success
  } finally {
    loading.value = false
  }
})

async function confirmStripePayment() {
  paying.value = true
  try {
    const { error } = await stripe.confirmPayment({
      elements,
      confirmParams: { return_url: window.location.href },
    })
    if (error) alert(error.message)
  } finally {
    paying.value = false
  }
}
</script>
