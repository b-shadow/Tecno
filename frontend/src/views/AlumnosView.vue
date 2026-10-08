<script setup>
import { computed, onMounted, ref } from 'vue'
import { FileUp, RefreshCw } from '@lucide/vue'
import ExportStatusBadge from '../components/ExportStatusBadge.vue'
import {
  actualizarExportacion,
  exportarAcademico,
  listExportaciones,
  listInscripciones,
  prepararExportacionAcademica,
} from '../services/api'

const inscripciones = ref([])
const preparacion = ref({ total: 0, inscripciones: [] })
const exportaciones = ref([])
const loading = ref(true)
const error = ref('')
const message = ref('')
const search = ref('')

const filteredStudents = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (!term) return inscripciones.value

  return inscripciones.value.filter((inscripcion) => [
    inscripcion.prospecto?.nombre,
    inscripcion.prospecto?.apellido,
    inscripcion.prospecto?.correo,
    inscripcion.solicitud_compra?.programa_nombre,
    inscripcion.solicitud_compra?.modulo_nombre,
  ].some((value) => String(value || '').toLowerCase().includes(term)))
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [inscripcionData, preparacionData, exportacionData] = await Promise.all([
      listInscripciones(),
      prepararExportacionAcademica(),
      listExportaciones(),
    ])
    inscripciones.value = inscripcionData
    preparacion.value = preparacionData
    exportaciones.value = exportacionData
  } catch (exception) {
    error.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudo cargar alumnos e integracion academica.'
  } finally {
    loading.value = false
  }
}

async function exportData() {
  message.value = ''
  error.value = ''
  try {
    const response = await exportarAcademico()
    downloadCsv(response.filas || [], response.archivo || 'alumnos_inscritos.csv')
    message.value = `${response.exportaciones.length} alumno(s) exportado(s) en CSV.`
    await load()
  } catch (exception) {
    error.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudo exportar la informacion.'
  }
}

function downloadCsv(rows, filename) {
  if (!rows.length) return

  const headers = Object.keys(rows[0])
  const csv = [
    headers.join(','),
    ...rows.map((row) => headers.map((header) => escapeCsv(row[header])).join(',')),
  ].join('\r\n')

  const blob = new Blob([`\ufeff${csv}`], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

function escapeCsv(value) {
  const text = String(value ?? '')

  if (/[",\r\n]/.test(text)) {
    return `"${text.replaceAll('"', '""')}"`
  }

  return text
}

async function updateStatus(exportacion, estado) {
  await actualizarExportacion(exportacion.id, { estado, respuesta: exportacion.respuesta })
  await load()
}

function fullName(prospecto) {
  return [prospecto?.nombre, prospecto?.apellido].filter(Boolean).join(' ') || 'Sin nombre'
}

function paymentState(inscripcion) {
  return inscripcion.solicitud_compra?.pago?.estado
    || inscripcion.solicitud_compra?.orden_item?.orden_pago?.pago?.estado
    || 'Pago aprobado'
}

function formatDate(value) {
  if (!value) return 'Sin fecha'
  return new Date(value).toLocaleString('es-BO')
}

onMounted(load)
</script>

<template>
  <section class="public-board">
    <section class="table-surface">
      <div class="table-header">
        <div>
          <p class="eyebrow">Alumnos e integracion academica</p>
          <h2>Alumnos inscritos</h2>
          <p>Gestiona alumnos confirmados y prepara su envio al sistema academico externo.</p>
        </div>
        <button class="secondary-button" type="button" @click="load">
          <RefreshCw :size="17" />
          Actualizar
        </button>
      </div>

      <section class="dashboard-grid">
        <article class="metric-card">
          <span>Alumnos inscritos</span>
          <strong>{{ inscripciones.length }}</strong>
          <p>Prospectos con inscripcion confirmada.</p>
        </article>
        <article class="metric-card">
          <span>Listos para exportar</span>
          <strong>{{ preparacion.total }}</strong>
          <p>Pagos aprobados pendientes de envio academico.</p>
        </article>
        <article class="metric-card">
          <span>Exportaciones historicas</span>
          <strong>{{ exportaciones.length }}</strong>
          <p>Registros preparados para el sistema externo.</p>
        </article>
      </section>

      <div class="filters">
        <input v-model="search" placeholder="Buscar alumno, correo, programa o modulo..." />
      </div>

      <p v-if="message" class="success-message">{{ message }}</p>
      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="loading" class="muted">Cargando alumnos...</p>
      <div class="form-actions">
        <button class="primary-inline" type="button" :disabled="preparacion.total === 0" @click="exportData">
          <FileUp :size="18" />
          Exportar alumnos
        </button>
      </div>
    </section>

    <section class="table-surface">
      <div class="table-header">
        <div>
          <p class="eyebrow">Alumnos</p>
          <h2>Inscripciones confirmadas</h2>
        </div>
      </div>
      <div v-if="!loading" class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Alumno</th>
              <th>Contacto</th>
              <th>Programa</th>
              <th>Modulo</th>
              <th>Pago</th>
              <th>Inscripcion</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="inscripcion in filteredStudents" :key="inscripcion.id">
              <td>{{ fullName(inscripcion.prospecto) }}</td>
              <td>
                {{ inscripcion.prospecto?.correo }}<br>
                <small>{{ inscripcion.prospecto?.telefono || 'Sin telefono' }}</small>
              </td>
              <td>{{ inscripcion.solicitud_compra?.programa_nombre }}</td>
              <td>{{ inscripcion.solicitud_compra?.modulo_nombre }}</td>
              <td><span class="badge">{{ paymentState(inscripcion) }}</span></td>
              <td>
                <ExportStatusBadge :estado="inscripcion.estado" /><br>
                <small>{{ formatDate(inscripcion.fecha_confirmacion) }}</small>
              </td>
            </tr>
            <tr v-if="filteredStudents.length === 0">
              <td colspan="6">No hay alumnos inscritos para mostrar.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="table-surface">
      <div class="table-header">
        <div>
          <p class="eyebrow">Preparacion</p>
          <h2>Alumnos listos para exportar</h2>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Alumno</th><th>Modulo</th><th>Pago</th><th>Estado</th></tr></thead>
          <tbody>
            <tr v-for="inscripcion in preparacion.inscripciones" :key="inscripcion.id">
              <td>{{ fullName(inscripcion.prospecto) }}</td>
              <td>{{ inscripcion.solicitud_compra?.modulo_nombre }}</td>
              <td>{{ paymentState(inscripcion) }}</td>
              <td><ExportStatusBadge :estado="inscripcion.estado" /></td>
            </tr>
            <tr v-if="preparacion.inscripciones.length === 0"><td colspan="4">Sin alumnos listos para exportar.</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="table-surface">
      <div class="table-header">
        <div>
          <p class="eyebrow">Historial</p>
          <h2>Envios al sistema academico</h2>
        </div>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Alumno</th><th>Usuario</th><th>Fecha</th><th>Estado</th><th>Acciones</th></tr></thead>
          <tbody>
            <tr v-for="exportacion in exportaciones" :key="exportacion.id">
              <td>{{ fullName(exportacion.prospecto) }}</td>
              <td>{{ exportacion.usuario?.nombre }} {{ exportacion.usuario?.apellido }}</td>
              <td>{{ formatDate(exportacion.fecha_exportacion) }}</td>
              <td><ExportStatusBadge :estado="exportacion.estado" /></td>
              <td class="row-actions">
                <button @click="updateStatus(exportacion, 'recibida')">Recibida</button>
                <button @click="updateStatus(exportacion, 'error')">Error</button>
              </td>
            </tr>
            <tr v-if="exportaciones.length === 0"><td colspan="5">Sin envios registrados.</td></tr>
          </tbody>
        </table>
      </div>
    </section>
  </section>
</template>
