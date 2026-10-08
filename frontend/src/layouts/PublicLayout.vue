<script setup>
import { onMounted, ref } from 'vue'
import HeaderBar from '../components/HeaderBar.vue'

const theme = ref(localStorage.getItem('crm_theme') || 'light')

function applyTheme() {
  document.documentElement.dataset.theme = theme.value
  localStorage.setItem('crm_theme', theme.value)
}

function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  applyTheme()
}

onMounted(applyTheme)
</script>

<template>
  <div class="app-shell public-shell">
    <div class="app-main">
      <HeaderBar :internal="false" :theme="theme" @toggle-theme="toggleTheme" />
      <main class="content-area">
        <slot />
      </main>
    </div>
  </div>
</template>
