<script setup>
import { onMounted, ref } from 'vue'
import HeaderBar from '../components/HeaderBar.vue'
import SidebarNav from '../components/SidebarNav.vue'

const sidebarCollapsed = ref(localStorage.getItem('crm_sidebar_collapsed') === '1')
const theme = ref(localStorage.getItem('crm_theme') || 'light')

function applyTheme() {
  document.documentElement.dataset.theme = theme.value
  localStorage.setItem('crm_theme', theme.value)
}

function toggleTheme() {
  theme.value = theme.value === 'dark' ? 'light' : 'dark'
  applyTheme()
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
  localStorage.setItem('crm_sidebar_collapsed', sidebarCollapsed.value ? '1' : '0')
}

onMounted(() => {
  applyTheme()
  if (window.matchMedia('(max-width: 960px)').matches) {
    sidebarCollapsed.value = true
  }
})
</script>

<template>
  <div class="app-shell" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
    <SidebarNav :collapsed="sidebarCollapsed" @toggle-sidebar="toggleSidebar" />
    <div class="app-main">
      <HeaderBar
        :internal="true"
        :sidebar-collapsed="sidebarCollapsed"
        :theme="theme"
        @toggle-theme="toggleTheme"
      />
      <main class="content-area">
        <slot />
      </main>
    </div>
  </div>
</template>
