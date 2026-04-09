import { createRouter, createWebHistory } from 'vue-router'
import { useAdminAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: () => import('@/views/LoginView.vue') },
    { path: '/auth/line/callback', name: 'line-callback', component: () => import('@/views/LineCallbackView.vue') },
    {
      path: '/',
      component: () => import('@/components/layout/AdminLayout.vue'),
      meta: { requiresAdmin: true },
      children: [
        { path: '', redirect: '/dashboard' },
        { path: 'dashboard', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
        { path: 'products', name: 'products', component: () => import('@/views/products/ProductListView.vue') },
        { path: 'products/new', name: 'product-new', component: () => import('@/views/products/ProductFormView.vue') },
        { path: 'products/:id/edit', name: 'product-edit', component: () => import('@/views/products/ProductFormView.vue') },
        { path: 'categories', name: 'categories', component: () => import('@/views/products/CategoryView.vue') },
        { path: 'orders', name: 'orders', component: () => import('@/views/orders/OrderListView.vue') },
        { path: 'orders/:id', name: 'order-detail', component: () => import('@/views/orders/OrderDetailView.vue') },
        { path: 'users', name: 'users', component: () => import('@/views/users/UserListView.vue') },
        { path: 'coupons', name: 'coupons', component: () => import('@/views/coupons/CouponView.vue') },
        { path: 'logistics', name: 'logistics', component: () => import('@/views/logistics/LogisticsView.vue') },
      ],
    },
  ],
})

router.beforeEach(async (to) => {
  if (to.meta.requiresAdmin) {
    const authStore = useAdminAuthStore()
    if (!authStore.isLoggedIn) {
      await authStore.fetchUser()
      if (!authStore.isLoggedIn) {
        return { name: 'login' }
      }
    }
  }
})

export default router
