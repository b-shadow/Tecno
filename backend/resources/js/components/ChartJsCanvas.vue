<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  type: { type: String, required: true },
  data: { type: Object, required: true },
  options: { type: Object, default: () => ({}) },
})

const canvas = ref(null)
let chart = null
let themeObserver = null

function readableColor(color, dark) {
  if (!dark) return color
  if (Array.isArray(color)) return color.map((item) => readableColor(item, dark))
  return ({ '#083456': '#79b7ee', '#0f5d78': '#5dcad5', '#101820': '#e6edf5' })[color] || color
}

async function renderChart() {
  await nextTick()
  if (!canvas.value) return

  const dark = document.documentElement.dataset.theme === 'dark'
  const color = dark ? '#dcebf3' : '#334155'
  const gridColor = dark ? 'rgba(220,235,243,0.16)' : 'rgba(8,52,86,0.12)'
  const options = {
    ...props.options,
    color,
    plugins: {
      ...props.options.plugins,
      legend: {
        ...props.options.plugins?.legend,
        labels: { ...props.options.plugins?.legend?.labels, color },
      },
    },
  }
  if (props.options.scales) {
    options.scales = Object.fromEntries(Object.entries(props.options.scales).map(([axis, settings]) => [axis, {
      ...settings,
      ticks: { ...settings.ticks, color },
      grid: { ...settings.grid, color: gridColor },
      border: { ...settings.border, color: gridColor },
    }]))
  }

  chart?.destroy()
  chart = new Chart(canvas.value, {
    type: props.type,
    data: {
      labels: [...props.data.labels],
      datasets: props.data.datasets.map((dataset) => ({
        ...dataset,
        data: [...dataset.data],
        backgroundColor: readableColor(dataset.backgroundColor, dark),
        borderColor: readableColor(dataset.borderColor, dark),
      })),
    },
    options,
  })
}

watch(() => [props.type, props.data, props.options], renderChart, { deep: true })

onMounted(() => {
  themeObserver = new MutationObserver(renderChart)
  themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
  renderChart()
})

onBeforeUnmount(() => {
  themeObserver?.disconnect()
  chart?.destroy()
})
</script>

<template>
  <canvas ref="canvas" role="img" :aria-label="data.datasets.map((item) => item.label).join(', ')"></canvas>
</template>
