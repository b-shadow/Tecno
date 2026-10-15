<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  type: { type: String, required: true },
  data: { type: Object, required: true },
  options: { type: Object, default: () => ({}) },
})

const canvas = ref(null)
let chart = null
let loader = null

function loadChart() {
  if (window.Chart) return Promise.resolve(window.Chart)
  if (loader) return loader

  loader = new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = '/vendor/chart.umd.js'
    script.onload = () => resolve(window.Chart)
    script.onerror = () => reject(new Error('No se pudo cargar Chart.js'))
    document.head.appendChild(script)
  })

  return loader
}

async function renderChart() {
  await nextTick()
  if (!canvas.value) return

  const Chart = await loadChart()
  chart?.destroy()
  chart = new Chart(canvas.value, {
    type: props.type,
    data: props.data,
    options: props.options,
  })
}

watch(() => [props.type, props.data, props.options], renderChart, { deep: true })

onMounted(renderChart)

onBeforeUnmount(() => {
  chart?.destroy()
})
</script>

<template>
  <canvas ref="canvas"></canvas>
</template>
