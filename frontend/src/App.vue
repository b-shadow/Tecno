<script setup>
import { computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import InternalLayout from './layouts/InternalLayout.vue'
import PublicLayout from './layouts/PublicLayout.vue'
import { authState, refreshSession } from './services/auth'

const route = useRoute()
const layout = computed(() => (authState.usuario && route.meta.private ? InternalLayout : PublicLayout))

onMounted(() => {
  refreshSession().catch(() => {})
})
</script>

<template>
  <component :is="layout">
    <RouterView />
  </component>
</template>
