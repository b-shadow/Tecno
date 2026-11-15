<script setup>
import { apiErrorMessage } from '../services/errors'
import { computed, onMounted, ref } from 'vue'
import { CheckCircle2, RefreshCw, X, XCircle } from '@lucide/vue'
import { aprobarPago, listPagos, rechazarPago } from '../services/api'

const pagos = ref([])
const estado = ref('En revision')
const observaciones = ref({})
const loading = ref(true)
const saving = ref({})
const message = ref('')
const error = ref('')
const receiptPreview = ref(null)

const filteredPagos = computed(() => pagos.value)

async function load() {
  loading.value = true
  error.value = ''
  try {
    pagos.value = await listPagos({ estado: estado.value })
  } catch (exception) {
    error.value = apiErrorMessage(exception, 'No se pudieron cargar los pagos.')
  } finally {
    loading.value = false
  }
}

function prospectName(pago) {
  const prospecto = pago.orden_pago?.prospecto
  return [prospecto?.nombre, prospecto?.apellido].filter(Boolean).join(' ') || 'Sin prospecto'
}

function modulesText(pago) {
  return pago.orden_pago?.items?.map((item) => item.modulo_nombre).join(', ') || 'Sin modulo'
}

function latestReceipt(pago) {
  return [...(pago.comprobantes || [])].sort((a, b) => b.id - a.id)[0] || null
}

function canApprove(pago) {
  return pago.estado === 'En revision' && Boolean(latestReceipt(pago))
}

function canReject(pago) {
  return pago.estado === 'En revision' && Boolean(latestReceipt(pago))
}

function paymentLabel(pago) {
  if (pago.estado === 'Pago aprobado') return 'Inscripcion confirmada'
  if (pago.estado === 'Pago rechazado') return 'Pago rechazado'
  if (pago.estado === 'En revision') return 'Comprobante en revision'
  return pago.estado
}

function money(value) {
  return `${Number(value || 0).toFixed(2)} Bs`
}

function formatDate(value) {
  if (!value) return 'No registrado'
  return new Date(value).toLocaleString('es-BO')
}

async function approve(pago) {
  message.value = ''
  error.value = ''
  saving.value[pago.id] = true
  try {
    const response = await aprobarPago(pago.id, observaciones.value[pago.id] || '')
    const total = response.inscripciones?.length || 0
    message.value = total
      ? `Pago aprobado. Se confirmo la inscripcion de ${prospectName(pago)} en ${total} modulo(s).`
      : 'Pago aprobado. Inscripcion confirmada.'
    await load()
  } catch (exception) {
    error.value = apiErrorMessage(exception, 'No se pudo aprobar el pago.')
  } finally {
    saving.value[pago.id] = false
  }
}

async function reject(pago) {
  message.value = ''
  error.value = ''
  saving.value[pago.id] = true
  try {
    await rechazarPago(pago.id, observaciones.value[pago.id] || 'Comprobante observado')
    message.value = 'Pago rechazado correctamente.'
    await load()
  } catch (exception) {
    error.value = apiErrorMessage(exception, 'No se pudo rechazar el pago.')
  } finally {
    saving.value[pago.id] = false
  }
}

onMounted(load)
</script>

<template>
  <section class="public-board">
    <section class="table-surface">
      <div class="table-header">
        <div>
          <p class="eyebrow">Validacion de pagos</p>
          <h2>Comprobantes recibidos</h2>
          <p>Aprueba comprobantes para confirmar automaticamente la inscripcion del alumno.</p>
        </div>
        <button class="secondary-button" type="button" @click="load">
          <RefreshCw :size="17" />
          Actualizar
        </button>
      </div>

      <div class="filters">
        <select v-model="estado" @change="load">
          <option value="">Todos</option>
          <option>En revision</option>
          <option>Pago aprobado</option>
          <option>Pago rechazado</option>
          <option>Pendiente de pago</option>
        </select>
      </div>

      <p v-if="message" class="success-message">{{ message }}</p>
      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="loading" class="muted">Cargando pagos...</p>

      <div v-if="!loading" class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Prospecto</th>
              <th>Modulos</th>
              <th>Monto</th>
              <th>Estado</th>
              <th>Comprobante</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="pago in filteredPagos" :key="pago.id">
              <td>{{ prospectName(pago) }}</td>
              <td>{{ modulesText(pago) }}</td>
              <td>{{ money(pago.monto) }}</td>
              <td>
                <span class="badge">{{ paymentLabel(pago) }}</span>
                <small v-if="pago.fecha_validacion"><br>Validado: {{ formatDate(pago.fecha_validacion) }}</small>
              </td>
              <td>
                <button v-if="latestReceipt(pago)" class="receipt-link" type="button" @click="receiptPreview = latestReceipt(pago)">{{ latestReceipt(pago).nombre_archivo || 'Ver comprobante' }}</button>
                <span v-else>Sin comprobante</span>
                <small v-if="latestReceipt(pago)">
                  <br>Remitente: {{ latestReceipt(pago).remitente || 'No registrado' }}
                  <br>Pago: {{ formatDate(latestReceipt(pago).hora_pago) }}
                </small>
              </td>
              <td class="row-actions">
                <input v-model="observaciones[pago.id]" :disabled="pago.estado !== 'En revision'" placeholder="Observacion" />
                <button :disabled="!canApprove(pago) || saving[pago.id]" @click="approve(pago)">
                  <CheckCircle2 :size="16" />
                  Aprobar e inscribir
                </button>
                <button :disabled="!canReject(pago) || saving[pago.id]" @click="reject(pago)">
                  <XCircle :size="16" />
                  Rechazar
                </button>
              </td>
            </tr>
            <tr v-if="filteredPagos.length === 0">
              <td colspan="6">No hay pagos para el filtro seleccionado.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
    <Teleport to="body">
      <div v-if="receiptPreview" class="modal-backdrop" @click.self="receiptPreview = null">
        <section class="modal-card receipt-viewer" role="dialog" aria-modal="true" aria-label="Vista del comprobante">
          <div class="modal-header">
            <h2>{{ receiptPreview.nombre_archivo || 'Comprobante' }}</h2>
            <button class="top-icon-button" type="button" title="Cerrar" @click="receiptPreview = null"><X :size="20" /></button>
          </div>
          <img v-if="receiptPreview.archivo?.startsWith('data:image/')" :src="receiptPreview.archivo" alt="Comprobante de pago presentado" />
          <iframe v-else-if="receiptPreview.mime === 'application/pdf'" :src="receiptPreview.archivo" title="Comprobante PDF"></iframe>
          <p v-else>Este archivo no tiene vista previa. Puedes descargarlo para revisarlo.</p>
          <a class="secondary-button" :href="receiptPreview.archivo" :download="receiptPreview.nombre_archivo || 'comprobante'">Descargar comprobante</a>
        </section>
      </div>
    </Teleport>
  </section>
</template>
