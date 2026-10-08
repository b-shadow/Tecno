<script setup>
import { onMounted, ref } from 'vue'
import { getSystemHealth } from '../services/api'

const health = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    health.value = await getSystemHealth()
  } catch {
    health.value = {
      status: 'backend no disponible',
      database: 'pendiente',
      architecture: 'MVC API + frontend Vue',
      domains: [
        'Seguridad y acceso',
        'Gestion academica comercial',
        'Captacion, compras y pagos',
        'Ventas, pagos y comisiones',
        'Reportes, comunicacion e integracion',
      ],
    }
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <section class="page-grid">
    <div class="intro-panel">
      <p class="eyebrow">Fase 0</p>
      <h2>Preparacion del proyecto y arquitectura base</h2>
      <p>
        Base lista para construir el CRM comercial educativo con Laravel, Vue.js,
        PostgreSQL y arquitectura MVC separada por dominios funcionales.
      </p>
    </div>

    <div class="status-panel">
      <h3>Estado de integracion</h3>
      <div v-if="loading" class="muted">Verificando API...</div>
      <dl v-else>
        <div>
          <dt>Backend</dt>
          <dd>{{ health.status }}</dd>
        </div>
        <div>
          <dt>Base de datos</dt>
          <dd>{{ health.database }}</dd>
        </div>
        <div>
          <dt>Arquitectura</dt>
          <dd>{{ health.architecture }}</dd>
        </div>
      </dl>
    </div>
  </section>

  <section class="module-list">
    <article v-for="module in health?.domains || []" :key="module" class="module-card">
      <span></span>
      <strong>{{ module }}</strong>
    </article>
  </section>
</template>
