<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], required: true },
  detail: { type: String, default: '' },
})
</script>

<template>
  <article class="metric-card">
    <span>{{ label }}</span>
    <strong>{{ value }}</strong>
    <p v-if="detail">{{ detail }}</p>
  </article>
</template>
