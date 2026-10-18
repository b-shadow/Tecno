<script setup>
import { computed, onMounted, ref } from 'vue'
import { BadgeDollarSign, Clock3, GraduationCap, MessageCircle, RefreshCw, UsersRound } from '@lucide/vue'
import ChartJsCanvas from '../components/ChartJsCanvas.vue'
import { getDashboardMetricas } from '../services/api'
import { authState } from '../services/auth'

const loading = ref(true)
const error = ref('')
const dashboard = ref({
  kpis: {},
  series: {
    cursos_por_dia: [],
    ingresos_por_dia: [],
    pagos_por_estado: [],
    prospectos_por_estado: [],
    modulos_mas_vendidos: [],
    vendedores_por_cursos: [],
    comisiones_por_vendedor: [],
    pagos_pendientes_por_vendedor: [],
  },
})

const palette = ['#083456', '#10aeb5', '#f21f2d', '#0f5d78', '#17c6bd', '#101820']
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        boxWidth: 8,
        padding: 10,
        usePointStyle: true,
        font: { size: 11 },
      },
    },
  },
}

const kpiCards = computed(() => [
  { label: 'Cursos esta semana', value: dashboard.value.kpis.cursos_semana || 0, detail: 'Inscripciones confirmadas', icon: GraduationCap, tone: 'blue' },
  { label: 'Ingresos esta semana', value: money(dashboard.value.kpis.ingresos_semana), detail: 'Pagos aprobados', icon: BadgeDollarSign, tone: 'green' },
  { label: 'Pagos en revision', value: dashboard.value.kpis.pagos_revision || 0, detail: 'Comprobantes pendientes', icon: Clock3, tone: 'orange' },
  { label: 'Intereses activos', value: dashboard.value.kpis.chats_abiertos || 0, detail: 'Seguimientos abiertos', icon: MessageCircle, tone: 'cyan' },
  { label: 'Alumnos inscritos', value: dashboard.value.kpis.alumnos_total || 0, detail: 'Total confirmado', icon: UsersRound, tone: 'teal' },
])

const coursesBarData = computed(() => ({
  labels: dashboard.value.series.cursos_por_dia.map((item) => item.label),
  datasets: [{
    label: 'Cursos registrados',
    data: dashboard.value.series.cursos_por_dia.map((item) => item.total),
    backgroundColor: '#083456',
    borderRadius: 8,
  }],
}))

const incomeLineData = computed(() => ({
  labels: dashboard.value.series.ingresos_por_dia.map((item) => item.label),
  datasets: [{
    label: 'Ingresos aprobados',
    data: dashboard.value.series.ingresos_por_dia.map((item) => item.total),
    borderColor: '#10aeb5',
    backgroundColor: 'rgba(16, 174, 181, 0.16)',
    fill: true,
    tension: 0.35,
    pointRadius: 4,
  }],
}))

const paymentDoughnutData = computed(() => doughnutData(dashboard.value.series.pagos_por_estado, 'Pagos'))
const prospectDoughnutData = computed(() => doughnutData(dashboard.value.series.prospectos_por_estado, 'Prospectos'))
const moduleBarData = computed(() => horizontalData(dashboard.value.series.modulos_mas_vendidos, 'Cursos vendidos', '#10aeb5'))
const sellerBarData = computed(() => horizontalData(dashboard.value.series.vendedores_por_cursos, 'Cursos por vendedor', '#083456'))
const commissionBarData = computed(() => horizontalData(dashboard.value.series.comisiones_por_vendedor, 'Comisiones generadas', '#0f5d78'))
const pendingSellerBarData = computed(() => horizontalData(dashboard.value.series.pagos_pendientes_por_vendedor, 'Pagos pendientes', '#f21f2d'))

const barOptions = computed(() => ({
  ...chartOptions,
  scales: {
    y: { beginAtZero: true, ticks: { precision: 0, font: { size: 11 } }, grid: { color: 'rgba(8, 52, 86, 0.12)' } },
    x: { grid: { display: false }, ticks: { font: { size: 11 } } },
  },
}))

const horizontalOptions = computed(() => ({
  ...chartOptions,
  indexAxis: 'y',
  scales: {
    x: { beginAtZero: true, ticks: { precision: 0, font: { size: 11 } }, grid: { color: 'rgba(8, 52, 86, 0.12)' } },
    y: { grid: { display: false }, ticks: { font: { size: 11 } } },
  },
}))

const lineOptions = computed(() => ({
  ...chartOptions,
  scales: {
    y: { beginAtZero: true, ticks: { font: { size: 11 } }, grid: { color: 'rgba(8, 52, 86, 0.12)' } },
    x: { grid: { display: false }, ticks: { font: { size: 11 } } },
  },
}))

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    dashboard.value = await getDashboardMetricas()
  } catch (exception) {
    error.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudo cargar el dashboard.'
  } finally {
    loading.value = false
  }
}

function money(value) {
  return `${Number(value || 0).toFixed(2)} Bs`
}

function doughnutData(items, label) {
  return {
    labels: items.map((item) => item.label),
    datasets: [{
      label,
      data: items.map((item) => item.total),
      backgroundColor: palette,
      borderWidth: 0,
    }],
  }
}

function horizontalData(items, label, color) {
  return {
    labels: items.map((item) => item.label),
    datasets: [{
      label,
      data: items.map((item) => item.total),
      backgroundColor: color,
      borderRadius: 8,
    }],
  }
}

onMounted(loadDashboard)
</script>

<template>
  <section class="public-board analytics-dashboard">
    <section class="table-surface analytics-hero">
      <div class="table-header">
        <div>
          <p class="eyebrow">Dashboard dinamico</p>
          <h2>Resumen comercial</h2>
          <p>{{ authState.usuario?.nombre }}, estos son los indicadores visuales del proceso comercial.</p>
        </div>
        <button class="secondary-button" type="button" @click="loadDashboard">
          <RefreshCw :size="17" />
          Actualizar
        </button>
      </div>
      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="loading" class="muted">Cargando dashboard...</p>
    </section>

    <section class="analytics-kpi-grid">
      <article v-for="card in kpiCards" :key="card.label" class="analytics-kpi-card" :class="card.tone">
        <div>
          <component :is="card.icon" :size="20" />
        </div>
        <span>{{ card.label }}</span>
        <strong>{{ card.value }}</strong>
        <small>{{ card.detail }}</small>
      </article>
    </section>

    <section class="analytics-grid-main">
      <article class="table-surface analytics-chart-card wide">
        <div class="table-header">
          <div>
            <p class="eyebrow">Ultimos 7 dias</p>
            <h2>Cursos registrados por dia</h2>
          </div>
        </div>
        <div class="chart-box tall">
          <ChartJsCanvas type="bar" :data="coursesBarData" :options="barOptions" />
        </div>
      </article>

      <article class="table-surface analytics-chart-card">
        <div class="table-header">
          <div>
            <p class="eyebrow">Pagos</p>
            <h2>Estados de pago</h2>
          </div>
        </div>
        <div class="chart-box">
          <ChartJsCanvas type="doughnut" :data="paymentDoughnutData" :options="chartOptions" />
        </div>
      </article>

      <article class="table-surface analytics-chart-card">
        <div class="table-header">
          <div>
            <p class="eyebrow">Ingresos</p>
            <h2>Ingresos aprobados</h2>
          </div>
        </div>
        <div class="chart-box">
          <ChartJsCanvas type="line" :data="incomeLineData" :options="lineOptions" />
        </div>
      </article>

      <article class="table-surface analytics-chart-card">
        <div class="table-header">
          <div>
            <p class="eyebrow">Prospectos</p>
            <h2>Estados comerciales</h2>
          </div>
        </div>
        <div class="chart-box">
          <ChartJsCanvas type="doughnut" :data="prospectDoughnutData" :options="chartOptions" />
        </div>
      </article>

      <article class="table-surface analytics-chart-card">
        <div class="table-header">
          <div>
            <p class="eyebrow">Cursos</p>
            <h2>Modulos mas vendidos</h2>
          </div>
        </div>
        <div class="chart-box">
          <ChartJsCanvas type="bar" :data="moduleBarData" :options="horizontalOptions" />
        </div>
      </article>

      <article class="table-surface analytics-chart-card">
        <div class="table-header">
          <div>
            <p class="eyebrow">Vendedores</p>
            <h2>Cursos vendidos por vendedor</h2>
          </div>
        </div>
        <div class="chart-box">
          <ChartJsCanvas type="bar" :data="sellerBarData" :options="horizontalOptions" />
        </div>
      </article>

      <article class="table-surface analytics-chart-card">
        <div class="table-header">
          <div>
            <p class="eyebrow">Comisiones</p>
            <h2>Comisiones por vendedor</h2>
          </div>
        </div>
        <div class="chart-box">
          <ChartJsCanvas type="bar" :data="commissionBarData" :options="horizontalOptions" />
        </div>
      </article>

      <article class="table-surface analytics-chart-card">
        <div class="table-header">
          <div>
            <p class="eyebrow">Pendientes</p>
            <h2>Pagos pendientes por vendedor</h2>
          </div>
        </div>
        <div class="chart-box">
          <ChartJsCanvas type="bar" :data="pendingSellerBarData" :options="horizontalOptions" />
        </div>
      </article>
    </section>
  </section>
</template>
