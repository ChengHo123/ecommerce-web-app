import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('@/components/layout/DefaultLayout.vue'),
      children: [
        { path: '', name: 'home', component: () => import('@/views/HomeView.vue') },
        { path: 'products', name: 'products', component: () => import('@/views/ProductListView.vue') },
        { path: 'products/:slug', name: 'product-detail', component: () => import('@/views/ProductDetailView.vue') },
        { path: 'cart', name: 'cart', component: () => import('@/views/CartView.vue') },
        {
          path: 'checkout',
          name: 'checkout',
          component: () => import('@/views/CheckoutView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'checkout/confirm',
          name: 'checkout-confirm',
          component: () => import('@/views/CheckoutConfirmView.vue'),
        },
        {
          path: 'orders',
          name: 'orders',
          component: () => import('@/views/OrderHistoryView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'orders/:id',
          name: 'order-detail',
          component: () => import('@/views/OrderDetailView.vue'),
          meta: { requiresAuth: true },
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/ProfileView.vue'),
          meta: { requiresAuth: true },
        },
      ],
    },
    { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
    { path: '/auth/line/callback', name: 'line-callback', component: () => import('@/views/auth/LineCallbackView.vue') },
    { path: '/:pathMatch(.*)*', name: 'not-found', component: () => import('@/views/NotFoundView.vue') },
  ],
})

router.beforeEach(async (to) => {
  if (to.meta.requiresAuth) {
    const authStore = useAuthStore()
    if (!authStore.isLoggedIn) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }
  }
})

export default router
