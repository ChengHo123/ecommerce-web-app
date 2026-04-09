<template>
  <div>
    <!-- KPI Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
      <div v-for="card in kpiCards" :key="card.label" class="bg-white rounded-xl p-5 shadow-sm">
        <p class="text-sm text-gray-500">{{ card.label }}</p>
        <p class="text-2xl font-bold mt-1">{{ card.value }}</p>
      </div>
    </div>

    <!-- Revenue Chart -->
    <div class="bg-white rounded-xl p-6 shadow-sm">
      <h2 class="font-semibold mb-4">近 6 個月營收</h2>
      <Bar v-if="chartData" :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart, BarElement, CategoryScale, LinearScale, Tooltip, Legend } from 'chart.js'
import api from '@/api'

Chart.register(BarElement, CategoryScale, LinearScale, Tooltip, Legend)

const stats = ref<any>(null)

const kpiCards = computed(() => {
  if (!stats.value) return []
  return [
    { label: '今日營收', value: `NT$ ${stats.value.today_revenue.toLocaleString()}` },
    { label: '本月營收', value: `NT$ ${stats.value.month_revenue.toLocaleString()}` },
    { label: '今日訂單', value: stats.value.today_orders },
    { label: '待出貨訂單', value: stats.value.pending_orders },
    { label: '會員人數', value: stats.value.total_users },
    { label: '低庫存商品', value: stats.value.low_stock_count },
  ]
})

const chartData = computed(() => {
  if (!stats.value?.monthly_revenue) return null
  return {
    labels: stats.value.monthly_revenue.map((d: any) => d.month),
    datasets: [{
      label: '營收 (NT$)',
      data: stats.value.monthly_revenue.map((d: any) => d.revenue),
      backgroundColor: 'rgba(34, 197, 94, 0.5)',
      borderColor: 'rgb(34, 197, 94)',
      borderWidth: 2,
    }],
  }
})

const chartOptions = {
  responsive: true,
  plugins: { legend: { display: false } },
}

onMounted(async () => {
  const { data } = await api.get('/api/v1/admin/dashboard')
  stats.value = data
})
</script>
