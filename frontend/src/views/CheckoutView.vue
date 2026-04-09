<template>
  <div class="max-w-4xl mx-auto px-4 py-8">
    <h1 class="text-2xl font-bold mb-6">結帳</h1>

    <div class="grid md:grid-cols-3 gap-8">
      <div class="md:col-span-2 space-y-6">
        <!-- Logistics Type -->
        <div class="bg-white rounded-xl p-6 shadow-sm">
          <h2 class="font-semibold mb-4">配送方式</h2>
          <div class="grid grid-cols-2 gap-3">
            <label :class="['flex items-center gap-3 p-4 border-2 rounded-xl cursor-pointer',
              form.logistics_type === 'home' ? 'border-primary-500 bg-primary-50' : 'border-gray-200']">
              <input type="radio" v-model="form.logistics_type" value="home" class="hidden" />
              <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              <span class="font-medium">宅配</span>
            </label>
            <label :class="['flex items-center gap-3 p-4 border-2 rounded-xl cursor-pointer',
              form.logistics_type === 'cvs' ? 'border-primary-500 bg-primary-50' : 'border-gray-200']">
              <input type="radio" v-model="form.logistics_type" value="cvs" class="hidden" />
              <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              <span class="font-medium">超商取貨</span>
            </label>
          </div>
        </div>

        <!-- Home Delivery Address -->
        <div v-if="form.logistics_type === 'home'" class="bg-white rounded-xl p-6 shadow-sm">
          <h2 class="font-semibold mb-4">收件地址</h2>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="text-sm text-gray-600 mb-1 block">收件人姓名</label>
              <input v-model="form.shipping_address.recipient_name" type="text"
                class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-400" />
            </div>
            <div>
              <label class="text-sm text-gray-600 mb-1 block">手機號碼</label>
              <input v-model="form.shipping_address.phone" type="tel"
                class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-400" />
            </div>
            <div>
              <label class="text-sm text-gray-600 mb-1 block">郵遞區號</label>
              <input v-model="form.shipping_address.postal_code" type="text"
                class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-400" />
            </div>
            <div>
              <label class="text-sm text-gray-600 mb-1 block">縣市</label>
              <input v-model="form.shipping_address.city" type="text"
                class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-400" />
            </div>
            <div>
              <label class="text-sm text-gray-600 mb-1 block">鄉鎮市區</label>
              <input v-model="form.shipping_address.district" type="text"
                class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-400" />
            </div>
            <div>
              <label class="text-sm text-gray-600 mb-1 block">地址</label>
              <input v-model="form.shipping_address.address" type="text"
                class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-400" />
            </div>
          </div>
        </div>

        <!-- CVS Selection -->
        <div v-if="form.logistics_type === 'cvs'" class="bg-white rounded-xl p-6 shadow-sm">
          <h2 class="font-semibold mb-4">選擇超商門市</h2>
          <div class="flex gap-3 mb-4">
            <button @click="openCvsMap('UNIMART')"
              :class="['px-4 py-2 rounded-lg border text-sm', form.cvs_type === 'UNIMART' ? 'border-primary-500 text-primary-600 bg-primary-50' : 'border-gray-300']">
              7-ELEVEN
            </button>
            <button @click="openCvsMap('FAMI')"
              :class="['px-4 py-2 rounded-lg border text-sm', form.cvs_type === 'FAMI' ? 'border-primary-500 text-primary-600 bg-primary-50' : 'border-gray-300']">
              全家 Family Mart
            </button>
          </div>
          <div v-if="form.cvs_store_name" class="bg-green-50 text-green-700 px-4 py-3 rounded-lg text-sm">
            已選門市：{{ form.cvs_store_name }} ({{ form.cvs_store_id }})
          </div>
          <p v-else class="text-gray-400 text-sm">請點選超商品牌後選擇門市</p>
        </div>

        <!-- Payment Method -->
        <div class="bg-white rounded-xl p-6 shadow-sm">
          <h2 class="font-semibold mb-4">付款方式</h2>
          <div class="space-y-3">
            <label :class="['flex items-center gap-3 p-4 border-2 rounded-xl cursor-pointer',
              form.payment_method === 'linepay' ? 'border-primary-500 bg-primary-50' : 'border-gray-200']">
              <input type="radio" v-model="form.payment_method" value="linepay" class="hidden" />
              <span class="font-medium">LINE Pay</span>
            </label>
            <label :class="['flex items-center gap-3 p-4 border-2 rounded-xl cursor-pointer',
              form.payment_method === 'stripe' ? 'border-primary-500 bg-primary-50' : 'border-gray-200']">
              <input type="radio" v-model="form.payment_method" value="stripe" class="hidden" />
              <span class="font-medium">Apple Pay / 信用卡</span>
            </label>
          </div>
        </div>

        <!-- Coupon -->
        <div class="bg-white rounded-xl p-6 shadow-sm">
          <h2 class="font-semibold mb-4">折扣碼</h2>
          <div class="flex gap-3">
            <input v-model="couponCode" type="text" placeholder="輸入折扣碼"
              class="flex-1 border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-400" />
            <button @click="validateCoupon" class="bg-gray-100 hover:bg-gray-200 px-4 py-2 rounded-lg text-sm">
              套用
            </button>
          </div>
          <p v-if="couponMessage" :class="['text-sm mt-2', couponValid ? 'text-green-600' : 'text-red-500']">
            {{ couponMessage }}
          </p>
        </div>

        <!-- Note -->
        <div class="bg-white rounded-xl p-6 shadow-sm">
          <label class="font-semibold block mb-2">備註</label>
          <textarea v-model="form.buyer_note" rows="3"
            class="w-full border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-400 resize-none"
            placeholder="有什麼需要備注的嗎？"></textarea>
        </div>
      </div>

      <!-- Order Summary -->
      <div class="bg-white rounded-xl p-6 shadow-sm h-fit">
        <h2 class="font-semibold text-lg mb-4">訂單摘要</h2>
        <div class="space-y-2 text-sm">
          <div v-for="item in cartStore.cart?.items" :key="item.id" class="flex justify-between">
            <span class="text-gray-500 truncate mr-2">{{ item.product_name }} x{{ item.quantity }}</span>
            <span class="shrink-0">NT$ {{ item.subtotal.toLocaleString() }}</span>
          </div>
        </div>
        <div class="border-t my-4"></div>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-500">小計</span>
            <span>NT$ {{ cartStore.total.toLocaleString() }}</span>
          </div>
          <div v-if="discountAmount > 0" class="flex justify-between text-green-600">
            <span>折扣</span>
            <span>- NT$ {{ discountAmount.toLocaleString() }}</span>
          </div>
        </div>
        <div class="border-t my-4"></div>
        <div class="flex justify-between font-bold text-lg">
          <span>合計</span>
          <span class="text-primary-600">NT$ {{ (cartStore.total - discountAmount).toLocaleString() }}</span>
        </div>
        <button @click="submitOrder" :disabled="submitting"
          class="block w-full mt-4 bg-primary-500 hover:bg-primary-600 text-white text-center font-semibold py-3 rounded-xl transition-colors disabled:opacity-50">
          {{ submitting ? '處理中...' : '確認訂單' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import { useCartStore } from '@/stores/cart'

const router = useRouter()
const cartStore = useCartStore()

const form = reactive({
  logistics_type: 'home',
  payment_method: 'linepay',
  shipping_address: {
    recipient_name: '',
    phone: '',
    postal_code: '',
    city: '',
    district: '',
    address: '',
  },
  cvs_store_id: '',
  cvs_store_name: '',
  cvs_type: '',
  buyer_note: '',
  coupon_code: '',
})

const couponCode = ref('')
const couponMessage = ref('')
const couponValid = ref(false)
const discountAmount = ref(0)
const submitting = ref(false)

async function validateCoupon() {
  try {
    const { data } = await api.post('/api/v1/coupons/validate', {
      code: couponCode.value,
      order_amount: cartStore.total,
    })
    couponValid.value = data.valid
    couponMessage.value = data.message
    discountAmount.value = data.valid ? data.discount_amount : 0
    if (data.valid) form.coupon_code = couponCode.value
  } catch {
    couponMessage.value = '驗證失敗'
  }
}

async function openCvsMap(cvsType: string) {
  form.cvs_type = cvsType
  const { data } = await api.get(`/api/v1/logistics/cvs-map-url?cvs_type=${cvsType}`)
  // Open in popup window; ECPay will call back via window.postMessage or redirect
  const popup = window.open(data.url, 'cvsmap', 'width=800,height=600')
  window.addEventListener('message', (e) => {
    if (e.data?.CVSStoreID) {
      form.cvs_store_id = e.data.CVSStoreID
      form.cvs_store_name = e.data.CVSStoreName
      popup?.close()
    }
  }, { once: true })
}

async function submitOrder() {
  submitting.value = true
  try {
    const payload: any = {
      logistics_type: form.logistics_type,
      payment_method: form.payment_method,
      buyer_note: form.buyer_note || null,
      coupon_code: form.coupon_code || null,
    }
    if (form.logistics_type === 'home') {
      payload.shipping_address = form.shipping_address
    } else {
      payload.cvs_store_id = form.cvs_store_id
      payload.cvs_store_name = form.cvs_store_name
      payload.cvs_type = form.cvs_type
    }

    const { data: order } = await api.post('/api/v1/orders', payload)
    await cartStore.clearCart()

    // Redirect to payment
    if (form.payment_method === 'linepay') {
      const { data: payData } = await api.post(`/api/v1/payment/linepay/request?order_id=${order.id}`)
      window.location.href = payData.payment_url
    } else {
      router.push({ name: 'checkout-confirm', query: { order_id: order.id } })
    }
  } catch (e: any) {
    alert(e.response?.data?.detail || '訂單建立失敗')
  } finally {
    submitting.value = false
  }
}
</script>
