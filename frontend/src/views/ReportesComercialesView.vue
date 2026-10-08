<script setup>
import { onMounted, ref } from 'vue'
import ChartCard from '../components/ChartCard.vue'
import ReportTable from '../components/ReportTable.vue'
import StatisticCard from '../components/StatisticCard.vue'
import { getReporteComercial } from '../services/api'

const reporte = ref(null)

onMounted(async () => {
  reporte.value = await getReporteComercial()
})
</script>

<template>
  <section v-if="reporte" class="public-board">
    <section class="dashboard-grid">
      <StatisticCard label="Nuevos" :value="reporte.indicadores.prospectos_nuevos" />
      <StatisticCard label="Contactados" :value="reporte.indicadores.prospectos_contactados" />
      <StatisticCard label="Convertidos" :value="reporte.indicadores.prospectos_convertidos" />
      <StatisticCard label="Perdidos" :value="reporte.indicadores.prospectos_perdidos" />
      <StatisticCard label="Intereses" :value="reporte.indicadores.intereses_registrados" />
      <StatisticCard label="Intereses asignados" :value="reporte.indicadores.conversaciones_asignadas" />
      <StatisticCard label="Conversion" :value="`${reporte.indicadores.tasa_conversion}%`" />
    </section>
    <ChartCard title="Estados comerciales" :items="reporte.estados.map((item) => ({ label: item.estado, total: item.total }))" />
    <ReportTable
      title="Rendimiento de vendedores"
      :rows="reporte.vendedores"
      :columns="[
        { key: 'nombre', label: 'Vendedor', format: (row) => `${row.nombre} ${row.apellido}` },
        { key: 'intereses_asignados_count', label: 'Intereses' },
        { key: 'comisiones_count', label: 'Cursos vendidos' },
        { key: 'interacciones_registradas_count', label: 'Interacciones' },
        { key: 'recordatorios_count', label: 'Recordatorios' },
      ]"
    />
  </section>
</template>
