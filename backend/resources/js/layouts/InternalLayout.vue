<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import HeaderBar from '../components/HeaderBar.vue'
import SidebarNav from '../components/SidebarNav.vue'

const sidebarCollapsed = ref(localStorage.getItem('crm_sidebar_collapsed') === '1')
const theme = ref(localStorage.getItem('crm_theme') || 'light')
const mobileQuery = window.matchMedia('(max-width: 960px)')

function syncSidebar(event) {
  sidebarCollapsed.value = event.matches || localStorage.getItem('crm_sidebar_collapsed') === '1'
}

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
  if (!mobileQuery.matches) localStorage.setItem('crm_sidebar_collapsed', sidebarCollapsed.value ? '1' : '0')
}

onMounted(() => {
  applyTheme()
  syncSidebar(mobileQuery)
  mobileQuery.addEventListener('change', syncSidebar)
})

onBeforeUnmount(() => mobileQuery.removeEventListener('change', syncSidebar))
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
      <main class="content-area" scroll-region>
        <slot />
      </main>
    </div>
  </div>
</template>
