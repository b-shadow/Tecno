<script setup>
import { onMounted, ref } from 'vue'
import StatisticCard from '../components/StatisticCard.vue'
import { getEstadisticasVendedor } from '../services/api'

const estadisticas = ref(null)

onMounted(async () => {
  estadisticas.value = await getEstadisticasVendedor()
})
</script>

<template>
  <section v-if="estadisticas" class="dashboard-grid">
    <StatisticCard label="Intereses asignados" :value="estadisticas.conversaciones_asignadas" />
    <StatisticCard label="Prospectos atendidos" :value="estadisticas.prospectos_atendidos" />
    <StatisticCard label="Interacciones realizadas" :value="estadisticas.interacciones_realizadas" />
    <StatisticCard label="Cursos vendidos" :value="estadisticas.ventas_logradas" />
    <StatisticCard label="Comisiones generadas" :value="`${estadisticas.comisiones_generadas} Bs`" />
    <StatisticCard label="Comisiones pendientes" :value="`${estadisticas.comisiones_pendientes} Bs`" />
    <StatisticCard label="Pendientes actuales" :value="estadisticas.pendientes_actuales" />
  </section>
</template>
