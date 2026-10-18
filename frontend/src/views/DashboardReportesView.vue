<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { FileText, RefreshCw, Search } from '@lucide/vue'
import { getReporteListado, listAnuncios, listUsuarios } from '../services/api'
import { authState, canManageCatalog, canManageUsers } from '../services/auth'

const reportTypes = [
  { id: 'prospectos', label: 'Prospectos', detail: 'Datos completos, estado e intereses registrados.' },
  { id: 'intereses', label: 'Intereses y agenda', detail: 'Seguimientos por modulo, programa y vendedor.' },
  { id: 'pagos', label: 'Pagos', detail: 'Ordenes, comprobantes y estados de pago.' },
  { id: 'alumnos', label: 'Alumnos inscritos', detail: 'Prospectos convertidos en alumnos por modulo.' },
  { id: 'comisiones', label: 'Comisiones', detail: 'Comisiones por curso vendido y estado de cobro.' },
  { id: 'vendedores', label: 'Vendedores', detail: 'Rendimiento comercial por asesor.' },
]

const estadosPorTipo = {
  prospectos: ['Nuevo', 'Contactado', 'Interesado', 'En proceso', 'Convertido', 'Perdido'],
  intereses: ['Nuevo', 'Contactado', 'Interesado', 'Pago enviado', 'En revision', 'Convertido', 'Perdido'],
  pagos: ['Pendiente de pago', 'En revision', 'Pago aprobado', 'Pago rechazado'],
  alumnos: ['Confirmada'],
  comisiones: ['Pendiente', 'Pagada'],
  vendedores: ['activo', 'inactivo'],
}

const selectedType = ref('prospectos')
const filtros = ref({ fecha_desde: '', fecha_hasta: '', programa_id: '', modulo_id: '', estado: '', vendedor_id: '', buscar: '' })
const programas = ref([])
const modulos = ref([])
const vendedores = ref([])
const report = ref({ titulo: '', columns: [], rows: [], total: 0 })
const loading = ref(true)
const error = ref('')

const selectedReport = computed(() => reportTypes.find((type) => type.id === selectedType.value) || reportTypes[0])
const canFilterSeller = computed(() => ['intereses', 'pagos', 'alumnos', 'comisiones', 'vendedores'].includes(selectedType.value) && authState.usuario?.rol !== 'vendedor')
const canFilterCatalog = computed(() => ['prospectos', 'intereses', 'pagos', 'alumnos', 'comisiones'].includes(selectedType.value))
const estadosDisponibles = computed(() => estadosPorTipo[selectedType.value] || [])

function cleanFilters() {
  return Object.fromEntries(Object.entries({
    tipo: selectedType.value,
    ...filtros.value,
  }).filter(([, value]) => value !== ''))
}

async function loadReport() {
  loading.value = true
  error.value = ''
  try {
    report.value = await getReporteListado(cleanFilters())
  } catch (exception) {
    error.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudo cargar el reporte.'
    report.value = { titulo: '', columns: [], rows: [], total: 0 }
  } finally {
    loading.value = false
  }
}

function resetFiltersForType() {
  filtros.value.estado = ''
  filtros.value.vendedor_id = ''
  filtros.value.buscar = ''
}

function cellClass(value) {
  const text = String(value || '')
  if (['Pago aprobado', 'Pagada', 'Confirmada', 'Convertido', 'activo', 'asignado'].includes(text)) return 'success'
  if (['Pendiente', 'Pendiente de pago', 'En revision', 'nuevo', 'En proceso'].includes(text)) return 'warning'
  if (['Pago rechazado', 'Perdido', 'inactivo'].includes(text)) return 'danger'
  return ''
}

watch(selectedType, async () => {
  resetFiltersForType()
  await loadReport()
})

onMounted(async () => {
  try {
    const anuncios = await listAnuncios()
    const programasMap = new Map()
    const modulosMap = new Map()
    anuncios.forEach((anuncio) => {
      if (anuncio.programa) programasMap.set(anuncio.programa.nombre, { id: anuncio.programa.nombre, nombre: anuncio.programa.nombre })
      if (anuncio.modulo) modulosMap.set(anuncio.external_modulo_id, { id: anuncio.external_modulo_id, nombre: anuncio.modulo.nombre, programa: anuncio.programa?.nombre })
    })
    programas.value = [...programasMap.values()]
    modulos.value = [...modulosMap.values()]

    if (canManageUsers() || canManageCatalog()) {
      vendedores.value = await listUsuarios({ rol: 'vendedor', estado: 'activo' }).catch(() => [])
    }
  } finally {
    await loadReport()
  }
})
</script>

<template>
  <section class="public-board reports-page">
    <section class="table-surface reports-header-panel">
      <div class="table-header">
        <div>
          <p class="eyebrow">Reportes</p>
          <h2>Listados comerciales</h2>
          <p>Selecciona un reporte, aplica filtros y consulta el detalle operativo.</p>
        </div>
        <button class="secondary-button" type="button" @click="loadReport">
          <RefreshCw :size="17" />
          Actualizar
        </button>
      </div>
      <p v-if="error" class="error-message">{{ error }}</p>
    </section>

    <section class="reports-layout">
      <aside class="table-surface reports-menu">
        <p class="eyebrow">Tipo de reporte</p>
        <button
          v-for="type in reportTypes"
          :key="type.id"
          type="button"
          :class="{ active: selectedType === type.id }"
          @click="selectedType = type.id"
        >
          <FileText :size="18" />
          <span>
            <strong>{{ type.label }}</strong>
            <small>{{ type.detail }}</small>
          </span>
        </button>
      </aside>

      <section class="table-surface report-results-panel">
        <div class="table-header">
          <div>
            <p class="eyebrow">{{ selectedReport.label }}</p>
            <h2>{{ report.titulo || selectedReport.label }}</h2>
          </div>
          <strong>{{ report.total }} registro(s)</strong>
        </div>

        <form class="report-query-grid" @submit.prevent="loadReport">
          <label>
            Desde
            <input v-model="filtros.fecha_desde" type="date" />
          </label>
          <label>
            Hasta
            <input v-model="filtros.fecha_hasta" type="date" />
          </label>
          <label v-if="canFilterCatalog">
            Programa
            <select v-model="filtros.programa_id">
              <option value="">Todos</option>
              <option v-for="programa in programas" :key="programa.id" :value="programa.id">{{ programa.nombre }}</option>
            </select>
          </label>
          <label v-if="canFilterCatalog">
            Modulo
            <select v-model="filtros.modulo_id">
              <option value="">Todos</option>
              <option v-for="modulo in modulos" :key="modulo.id" :value="modulo.id">{{ modulo.nombre }}</option>
            </select>
          </label>
          <label v-if="estadosDisponibles.length">
            Estado
            <select v-model="filtros.estado">
              <option value="">Todos</option>
              <option v-for="estado in estadosDisponibles" :key="estado" :value="estado">{{ estado }}</option>
            </select>
          </label>
          <label v-if="canFilterSeller">
            Vendedor
            <select v-model="filtros.vendedor_id">
              <option value="">Todos</option>
              <option v-for="vendedor in vendedores" :key="vendedor.id" :value="vendedor.id">{{ vendedor.nombre }} {{ vendedor.apellido }}</option>
            </select>
          </label>
          <label class="report-search-field">
            Buscar
            <span>
              <Search :size="17" />
              <input v-model="filtros.buscar" placeholder="Nombre, correo, CI, modulo..." />
            </span>
          </label>
          <button class="primary-inline" type="submit">Aplicar filtros</button>
        </form>

        <p v-if="loading" class="muted">Cargando reporte...</p>
        <div v-else class="table-wrap reports-table-wrap">
          <table class="reports-table">
            <thead>
              <tr>
                <th v-for="column in report.columns" :key="column.key">{{ column.label }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in report.rows" :key="index">
                <td v-for="column in report.columns" :key="column.key">
                  <span v-if="cellClass(row[column.key])" class="badge" :class="cellClass(row[column.key])">{{ row[column.key] }}</span>
                  <span v-else>{{ row[column.key] || '-' }}</span>
                </td>
              </tr>
              <tr v-if="report.rows.length === 0">
                <td :colspan="report.columns.length || 1">Sin registros para los filtros seleccionados.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </section>
  </section>
</template>
