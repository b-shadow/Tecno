<script setup>
import { computed, onMounted, watch } from 'vue'
import InternalLayout from './InternalLayout.vue'
import PublicLayout from './PublicLayout.vue'
import { authState, refreshSession } from '../services/auth'
import { go, useAppRoute } from '../services/navigation'
import { redirectFor, routeMeta } from '../access'

const route = useAppRoute()
const redirect = computed(() => redirectFor(route.value))
const layout = computed(() => (authState.usuario && routeMeta[route.value.path]?.private ? InternalLayout : PublicLayout))

// No se monta la pagina mientras haya que redirigir: evita llamadas a la API sin permiso.
watch(() => [route.value.fullPath, redirect.value], ([, target]) => {
  if (target) go(target, { replace: true })
}, { immediate: true })

onMounted(() => {
  refreshSession().catch(() => {})
})
</script>

<template>
  <component :is="layout">
    <slot v-if="!redirect" />
  </component>
</template>
