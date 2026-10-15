<script setup>
defineProps({
  estado: { type: String, required: true },
})
</script>

<template>
  <span class="badge" :class="estado">{{ estado }}</span>
</template>
