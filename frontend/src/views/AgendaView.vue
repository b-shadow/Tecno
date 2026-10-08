<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { CalendarPlus, CheckCircle2, ChevronRight, CreditCard, ExternalLink, FileCheck2, FileText, Filter, Info, Mail, MessageSquareText, Phone, Plus, RefreshCw, Search, Upload, X } from '@lucide/vue'
import {
  crearOrdenPago,
  crearRecordatorio,
  generarPagoOrden,
  listDescuentos,
  listIntereses,
  listOfertas,
  completarRecordatorio,
  registrarInteraccion,
  subirComprobante,
} from '../services/api'
import { authState } from '../services/auth'

const route = useRoute()
const intereses = ref([])
const ofertas = ref([])
const descuentos = ref([])
const selectedId = ref(null)
const loading = ref(true)
const error = ref('')
const message = ref('')
const searchTerm = ref('')
const historyModalOpen = ref(false)
const reminderModalOpen = ref(false)
const prospectModalOpen = ref(false)
const detailItem = ref(null)
const historyForm = ref({ tipo: 'WhatsApp', fecha: '', hora: '', descripcion: '', resultado: '' })
const reminderForm = ref({ fecha_programada: '', descripcion: '' })
const orderModalOpen = ref(false)
const selectedProgram = ref('')
const orderForm = ref({ modulos: [], descuentos: [] })
const receiptOrder = ref(null)
const receiptForm = ref({ archivo: '', nombre_archivo: '', mime: '', remitente: '', hora_pago: '', observacion: '' })
const DEFAULT_PAYMENT_QR = '/pagos/qr-pago-crm.svg'

const selectedInterest = computed(() => intereses.value.find((item) => item.id === selectedId.value) || null)
const selectedOrders = computed(() => selectedInterest.value?.ordenes_pago || selectedInterest.value?.ordenesPago || [])
const selectedReminders = computed(() => selectedInterest.value?.recordatorios || [])
const upcomingReminders = computed(() => [...selectedReminders.value]
  .filter((item) => ['Pendiente', 'Atrasada'].includes(item.estado))
  .sort((a, b) => new Date(a.fecha_programada) - new Date(b.fecha_programada)))
const contactHistory = computed(() => [...(selectedInterest.value?.interacciones || [])]
  .sort((a, b) => new Date(b.fecha || b.created_at) - new Date(a.fecha || a.created_at)))
const visibleInterests = computed(() => {
  const term = searchTerm.value.trim().toLowerCase()
  let base = intereses.value.filter((item) => item.vendedor_id)

  if (authState.usuario?.rol === 'vendedor') {
    base = intereses.value.filter((item) => item.vendedor_id === authState.usuario?.id)
  }

  if (!term) return base

  return base.filter((item) => [
    fullName(item.prospecto),
    item.prospecto?.correo,
    item.prospecto?.telefono,
    item.programa_nombre,
    item.modulo_nombre,
    item.estado,
  ].some((value) => String(value || '').toLowerCase().includes(term)))
})

const programOptions = computed(() => {
  const programs = new Map()
  ofertas.value.forEach((oferta) => {
    const name = oferta.programa?.nombre || oferta.modulo?.programa?.nombre
    if (!name) return
    if (!programs.has(name)) programs.set(name, { nombre: name, modulos: [] })
    programs.get(name).modulos.push(oferta.modulo)
  })
  return [...programs.values()]
})

const moduleOptions = computed(() => {
  if (!selectedProgram.value) return []
  return ofertas.value
    .filter((oferta) => (oferta.programa?.nombre || oferta.modulo?.programa?.nombre) === selectedProgram.value)
    .map((oferta) => oferta.modulo)
})

const canManageSelected = computed(() => {
  if (!selectedInterest.value) return false
  if (['administrador', 'coordinador'].includes(authState.usuario?.rol)) return true
  return selectedInterest.value.vendedor_id === authState.usuario?.id
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [interestData, offerData, discountData] = await Promise.all([
      listIntereses(),
      listOfertas().catch(() => []),
      listDescuentos().catch(() => []),
    ])
    intereses.value = interestData
    ofertas.value = offerData
    descuentos.value = discountData
    const queryId = Number(route.query.interes)
    if (queryId && visibleInterests.value.some((item) => item.id === queryId)) {
      selectedId.value = queryId
    } else if (!visibleInterests.value.some((item) => item.id === selectedId.value)) {
      selectedId.value = visibleInterests.value[0]?.id || null
    }
  } catch (exception) {
    error.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudo cargar la agenda comercial.'
  } finally {
    loading.value = false
  }
}

function whatsAppUrl(interes) {
  const digits = String(interes?.prospecto?.telefono || '').replace(/\D/g, '')
  const phone = digits.startsWith('591') ? digits : `591${digits}`
  const text = `Hola ${interes?.prospecto?.nombre || ''}, te escribo por tu interes en ${interes?.modulo_nombre}.`
  return `https://wa.me/${phone}?text=${encodeURIComponent(text)}`
}

function resetHistoryForm() {
  const now = new Date()
  historyForm.value = {
    tipo: 'WhatsApp',
    fecha: toDateInput(now),
    hora: toTimeInput(now),
    descripcion: '',
    resultado: '',
  }
}

function openHistoryModal() {
  if (!canManageSelected.value) return
  resetHistoryForm()
  historyModalOpen.value = true
}

function openReminderModal() {
  if (!canManageSelected.value) return
  reminderForm.value = { fecha_programada: '', descripcion: '' }
  reminderModalOpen.value = true
}

async function saveHistory() {
  if (!selectedInterest.value) return
  error.value = ''
  message.value = ''
  try {
    await registrarInteraccion({
      interes_id: selectedInterest.value.id,
      tipo: historyForm.value.tipo,
      descripcion: historyForm.value.descripcion,
      resultado: historyForm.value.resultado,
      fecha: buildDateTime(historyForm.value.fecha, historyForm.value.hora),
    })
    historyModalOpen.value = false
    message.value = 'Contacto registrado en la bitacora.'
    await load()
  } catch (exception) {
    error.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudo registrar el contacto.'
  }
}

async function saveReminder() {
  if (!selectedInterest.value) return
  error.value = ''
  message.value = ''
  try {
    await crearRecordatorio({
      interes_id: selectedInterest.value.id,
      fecha_programada: reminderForm.value.fecha_programada,
      descripcion: reminderForm.value.descripcion,
    })
    reminderModalOpen.value = false
    message.value = 'Actividad agendada correctamente.'
    await load()
  } catch (exception) {
    error.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudo registrar la actividad.'
  }
}

function openDetail(kind, item) {
  detailItem.value = { kind, item }
}

async function completeReminder(recordatorio) {
  error.value = ''
  try {
    await completarRecordatorio(recordatorio.id)
    message.value = 'Actividad marcada como realizada.'
    detailItem.value = null
    await load()
  } catch (exception) {
    error.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudo completar la actividad.'
  }
}

function openOrderModal() {
  if (!selectedInterest.value) return
  selectedProgram.value = selectedInterest.value.programa_nombre
  orderForm.value = { modulos: [selectedInterest.value.external_modulo_id], descuentos: [] }
  orderModalOpen.value = true
}

function selectFullProgram() {
  orderForm.value.modulos = moduleOptions.value.map((modulo) => modulo.external_modulo_id)
  const discount = descuentos.value.find((item) => item.codigo === 'PROGRAMA_COMPLETO')
  if (discount && !orderForm.value.descuentos.includes(discount.id)) orderForm.value.descuentos.push(discount.id)
}

async function createOrder() {
  if (!selectedInterest.value) return
  error.value = ''
  try {
    const orden = await crearOrdenPago(selectedInterest.value.id, orderForm.value)
    await generarPagoOrden(orden.id).catch(() => null)
    orderModalOpen.value = false
    message.value = 'Orden generada. Envia el QR al prospecto por WhatsApp y registra el comprobante cuando te lo remita.'
    await load()
  } catch (exception) {
    error.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudo crear la orden.'
  }
}

function openReceiptModal(orden) {
  receiptOrder.value = orden
  receiptForm.value = { archivo: '', nombre_archivo: '', mime: '', remitente: '', hora_pago: '', observacion: '' }
}

function latestReceipt(orden) {
  return orden?.pago?.comprobantes?.[0] || null
}

function canUploadReceipt(orden) {
  return orden?.pago && !latestReceipt(orden) && !['Pago aprobado', 'En revision'].includes(orden.pago.estado)
}

function handleReceipt(event) {
  const file = event.target.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    receiptForm.value.archivo = reader.result
    receiptForm.value.nombre_archivo = file.name
    receiptForm.value.mime = file.type
  }
  reader.readAsDataURL(file)
}

function isReceiptImage() {
  return receiptForm.value.archivo && String(receiptForm.value.mime || '').startsWith('image/')
}

async function uploadReceipt() {
  error.value = ''
  try {
    await subirComprobante({ pago_id: receiptOrder.value.pago.id, ...receiptForm.value })
    receiptOrder.value = null
    message.value = 'Comprobante registrado y enviado a revision.'
    await load()
  } catch (exception) {
    error.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudo registrar el comprobante.'
  }
}

function fullName(person) {
  return [person?.nombre, person?.apellido].filter(Boolean).join(' ') || 'Sin nombre'
}

function initials(person) {
  return fullName(person).split(' ').slice(0, 2).map((part) => part[0]).join('').toUpperCase()
}

function money(value) {
  return `${Number(value || 0).toFixed(2)} Bs`
}

function dateTime(value) {
  if (!value) return 'Sin fecha'
  return new Date(value).toLocaleString('es-BO', {
    day: 'numeric',
    month: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function shortDateTime(value) {
  if (!value) return 'Sin fecha'
  return new Date(value).toLocaleString('es-BO', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

function toDateInput(date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function toTimeInput(date) {
  return `${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

function buildDateTime(date, time) {
  if (!date || !time) return new Date().toISOString()
  return `${date}T${time}:00`
}

function lastActivity(interes) {
  return interes.interacciones?.[0]?.descripcion || 'Sin actividades registradas.'
}

watch(visibleInterests, (items) => {
  if (!items.some((item) => item.id === selectedId.value)) selectedId.value = items[0]?.id || null
})

onMounted(load)
</script>

<template>
  <section class="chat-page redesigned-chat agenda-page">
    <aside class="chat-list-panel">
      <div class="table-header">
        <div>
          <p class="eyebrow">Agenda comercial</p>
          <h2>Agenda</h2>
          <p>Seguimiento de interesados en nuestros cursos.</p>
        </div>
        <RouterLink class="primary-inline agenda-add-button" to="/interesados">
          <Plus :size="18" />
          Agregar
        </RouterLink>
      </div>

      <div class="agenda-search-row">
        <label class="chat-search">
          <Search :size="20" />
          <input v-model="searchTerm" placeholder="Buscar por nombre, curso o estado..." />
        </label>
        <button class="top-icon-button" type="button" title="Actualizar" @click="load">
          <RefreshCw :size="18" />
        </button>
        <button class="top-icon-button" type="button" title="Filtrar">
          <Filter :size="18" />
        </button>
      </div>

      <p v-if="message" class="success-message chat-notice">{{ message }}</p>
      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="loading" class="muted">Cargando agenda...</p>

      <button
        v-for="interes in visibleInterests"
        :key="interes.id"
        class="chat-list-item"
        :class="{ active: selectedId === interes.id }"
        type="button"
        @click="selectedId = interes.id"
      >
        <span class="chat-avatar">
          {{ initials(interes.prospecto) }}
          <i :class="{ muted: !interes.vendedor_id }"></i>
        </span>
        <span class="chat-list-content">
          <span class="chat-list-top">
            <strong>{{ fullName(interes.prospecto) }}</strong>
            <small>{{ interes.estado }}</small>
          </span>
          <small>{{ interes.modulo_nombre }} - {{ interes.vendedor ? fullName(interes.vendedor) : 'Sin vendedor' }}</small>
          <em>Ultima interaccion: {{ shortDateTime(interes.ultima_actividad_en || interes.created_at) }}</em>
        </span>
        <ChevronRight class="agenda-list-arrow" :size="22" />
      </button>

      <p v-if="!loading && visibleInterests.length === 0" class="muted">No hay intereses en seguimiento.</p>
    </aside>

    <section v-if="selectedInterest" class="chat-window agenda-detail-window">
      <header class="agenda-profile-card">
        <div class="agenda-profile-top">
          <span class="chat-avatar large">
            {{ initials(selectedInterest.prospecto) }}
            <i :class="{ muted: !selectedInterest.vendedor_id }"></i>
          </span>
          <div class="agenda-profile-copy">
            <h2>{{ fullName(selectedInterest.prospecto) }}</h2>
            <p>Interesado en: <strong>{{ selectedInterest.modulo_nombre }}</strong></p>
            <p>Ultima interaccion: {{ shortDateTime(selectedInterest.ultima_actividad_en || selectedInterest.created_at) }}</p>
            <div class="chat-status-row">
              <span class="chat-chip prospect">{{ selectedInterest.estado }}</span>
              <span class="chat-chip">{{ selectedInterest.vendedor ? fullName(selectedInterest.vendedor) : 'Sin vendedor' }}</span>
            </div>
          </div>
          <div class="agenda-profile-actions">
            <a class="secondary-button compact-chat-action whatsapp-action" :href="whatsAppUrl(selectedInterest)" target="_blank" rel="noreferrer">
            <ExternalLink :size="18" />
            WhatsApp
            </a>
            <button class="secondary-button compact-chat-action" type="button" @click="prospectModalOpen = true">
              <Info :size="18" />
              Ver datos
            </button>
          </div>
        </div>

        <div class="agenda-contact-strip">
          <article>
            <Mail :size="26" />
            <span>Correo</span>
            <strong>{{ selectedInterest.prospecto?.correo || 'Sin correo' }}</strong>
          </article>
          <article>
            <Phone :size="26" />
            <span>Telefono</span>
            <strong>{{ selectedInterest.prospecto?.telefono ? `+591 ${selectedInterest.prospecto.telefono}` : 'Sin telefono' }}</strong>
          </article>
          <article>
            <FileText :size="26" />
            <span>Notas</span>
            <strong>{{ lastActivity(selectedInterest) }}</strong>
          </article>
        </div>
      </header>

      <div class="agenda-content">
        <section class="agenda-columns">
          <section class="table-surface agenda-reminders">
            <div class="table-header compact-header">
              <div>
                <h3><CalendarPlus :size="24" /> Proximas veces a contactar</h3>
              </div>
              <button v-if="canManageSelected" class="primary-inline agenda-panel-action" type="button" @click="openReminderModal">
                <Plus :size="17" />
                Registrar actividad
              </button>
            </div>
            <div class="agenda-record-list">
              <button v-for="recordatorio in upcomingReminders" :key="recordatorio.id" class="agenda-record-row" type="button" @click="openDetail('recordatorio', recordatorio)">
                <span class="badge" :class="{ danger: recordatorio.estado === 'Atrasada', warning: recordatorio.estado === 'Pendiente' }">{{ recordatorio.estado }}</span>
                <strong>{{ dateTime(recordatorio.fecha_programada) }}</strong>
                <small>{{ recordatorio.descripcion }}</small>
              </button>
              <p v-if="!upcomingReminders.length" class="muted">Sin actividades futuras pendientes.</p>
            </div>
          </section>

          <section class="table-surface agenda-orders">
            <div class="table-header compact-header">
              <div>
                <h3><CreditCard :size="24" /> Ordenes y pagos</h3>
              </div>
              <button v-if="canManageSelected && authState.usuario?.rol === 'vendedor'" class="primary-inline agenda-panel-action" type="button" @click="openOrderModal">
                <CreditCard :size="17" />
                Crear orden
              </button>
            </div>
            <button v-for="orden in selectedOrders" :key="orden.id" class="payment-list-row agenda-order-row" type="button" @click="openReceiptModal(orden)">
              <div>
                <strong>{{ orden.pago?.estado || orden.estado }}</strong>
                <span>{{ orden.items?.length || 0 }} modulo(s) - {{ money(orden.total) }}</span>
                <small v-if="orden.estado !== (orden.pago?.estado || orden.estado)">{{ orden.estado }}</small>
              </div>
              <ChevronRight :size="20" />
            </button>
            <p v-if="!selectedOrders.length" class="muted">Aun no hay ordenes generadas.</p>
          </section>
        </section>

        <section class="table-surface agenda-timeline">
          <div class="table-header compact-header">
            <div>
              <h3><MessageSquareText :size="24" /> Historial de actividades</h3>
            </div>
            <button v-if="canManageSelected" class="primary-inline agenda-panel-action" type="button" @click="openHistoryModal">
              <Plus :size="17" />
              Registrar contacto
            </button>
          </div>
          <div class="agenda-history-table">
            <table v-if="contactHistory.length">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Tipo</th>
                  <th>Descripcion</th>
                  <th>Usuario</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="actividad in contactHistory" :key="actividad.id" @click="openDetail('interaccion', actividad)">
                  <td>{{ shortDateTime(actividad.fecha || actividad.created_at) }}</td>
                  <td><span class="badge">{{ actividad.tipo }}</span></td>
                  <td>{{ actividad.descripcion }}</td>
                  <td>{{ fullName(actividad.usuario) }}</td>
                </tr>
              </tbody>
            </table>
            <p v-if="!contactHistory.length" class="muted">Sin actividades registradas.</p>
          </div>
        </section>
      </div>
    </section>

    <section v-else class="table-surface">
      <p class="muted">Selecciona un interes para gestionar su seguimiento.</p>
    </section>

    <Teleport to="body">
      <div v-if="prospectModalOpen" class="modal-backdrop" @click.self="prospectModalOpen = false">
        <section class="modal-card agenda-action-modal">
          <div class="modal-header">
            <div>
              <p class="eyebrow">Datos del prospecto</p>
              <h2>{{ fullName(selectedInterest.prospecto) }}</h2>
              <p class="muted">Informacion de contacto registrada para este interes.</p>
            </div>
            <button class="top-icon-button" type="button" title="Cerrar" @click="prospectModalOpen = false">
              <X :size="20" />
            </button>
          </div>
          <dl class="prospect-detail-grid">
            <div><dt>Correo</dt><dd>{{ selectedInterest.prospecto?.correo || 'Sin correo' }}</dd></div>
            <div><dt>Telefono</dt><dd>{{ selectedInterest.prospecto?.telefono ? `+591 ${selectedInterest.prospecto.telefono}` : 'Sin telefono' }}</dd></div>
            <div><dt>CI</dt><dd>{{ selectedInterest.prospecto?.documento || 'Sin CI' }}</dd></div>
            <div><dt>Profesion</dt><dd>{{ selectedInterest.prospecto?.profesion || 'Sin profesion' }}</dd></div>
            <div><dt>Ubicacion</dt><dd>{{ selectedInterest.prospecto?.ubicacion || 'Sin ubicacion' }}</dd></div>
            <div><dt>Proximo contacto</dt><dd>{{ dateTime(selectedInterest.proximo_contacto) }}</dd></div>
            <div class="full-field"><dt>Interes</dt><dd>{{ selectedInterest.programa_nombre }} - {{ selectedInterest.modulo_nombre }}</dd></div>
          </dl>
          <div class="form-actions">
            <button class="secondary-button" type="button" @click="prospectModalOpen = false">Cerrar</button>
          </div>
        </section>
      </div>

      <div v-if="historyModalOpen" class="modal-backdrop" @click.self="historyModalOpen = false">
        <form class="modal-card agenda-action-modal" @submit.prevent="saveHistory">
          <div class="modal-header">
            <div>
              <p class="eyebrow">Bitacora comercial</p>
              <h2>Registrar contacto</h2>
              <p class="muted">Guarda lo conversado por WhatsApp, llamada u otro canal externo.</p>
            </div>
            <button class="top-icon-button" type="button" title="Cerrar" @click="historyModalOpen = false">
              <X :size="20" />
            </button>
          </div>
          <div class="form-grid">
            <label>
              Fecha
              <input v-model="historyForm.fecha" type="date" required />
            </label>
            <label>
              Hora
              <input v-model="historyForm.hora" type="time" required />
            </label>
            <label class="full-field">
              Tipo de conversacion
              <select v-model="historyForm.tipo">
                <option>WhatsApp</option>
                <option>Llamada</option>
                <option>Correo electronico</option>
                <option>Reunion</option>
                <option>Nota comercial</option>
                <option>Orden de pago enviada</option>
                <option>Pago informado</option>
                <option>Compra validada</option>
                <option>Orden finalizada</option>
              </select>
            </label>
            <label class="full-field">
              Descripcion
              <textarea v-model="historyForm.descripcion" required placeholder="Describe que se converso o que paso con el prospecto."></textarea>
            </label>
            <label class="full-field">
              Resultado
              <input v-model="historyForm.resultado" placeholder="Ej. Pide llamada el viernes, acepta descuento, queda pendiente..." />
            </label>
          </div>
          <div class="form-actions">
            <button type="submit" :disabled="!historyForm.descripcion.trim()">
              <MessageSquareText :size="18" />
              Guardar contacto
            </button>
            <button class="secondary-button" type="button" @click="historyModalOpen = false">Cancelar</button>
          </div>
        </form>
      </div>

      <div v-if="reminderModalOpen" class="modal-backdrop" @click.self="reminderModalOpen = false">
        <form class="modal-card agenda-action-modal" @submit.prevent="saveReminder">
          <div class="modal-header">
            <div>
              <p class="eyebrow">Agenda comercial</p>
              <h2>Registrar actividad</h2>
              <p class="muted">Programa una accion futura para contactar nuevamente al prospecto.</p>
            </div>
            <button class="top-icon-button" type="button" title="Cerrar" @click="reminderModalOpen = false">
              <X :size="20" />
            </button>
          </div>
          <div class="form-grid">
            <label class="full-field">
              Fecha y hora pactada
              <input v-model="reminderForm.fecha_programada" type="datetime-local" required />
            </label>
            <label class="full-field">
              Actividad pendiente
              <textarea v-model="reminderForm.descripcion" required placeholder="Ej. Llamar para confirmar pago o resolver dudas del modulo."></textarea>
            </label>
          </div>
          <div class="form-actions">
            <button type="submit" :disabled="!reminderForm.fecha_programada || !reminderForm.descripcion.trim()">
              <CalendarPlus :size="18" />
              Agendar actividad
            </button>
            <button class="secondary-button" type="button" @click="reminderModalOpen = false">Cancelar</button>
          </div>
        </form>
      </div>

      <div v-if="detailItem" class="modal-backdrop" @click.self="detailItem = null">
        <section class="modal-card agenda-action-modal">
          <div class="modal-header">
            <div>
              <p class="eyebrow">{{ detailItem.kind === 'recordatorio' ? 'Detalle de actividad' : 'Detalle de contacto' }}</p>
              <h2>{{ detailItem.kind === 'recordatorio' ? detailItem.item.estado : detailItem.item.tipo }}</h2>
            </div>
            <button class="top-icon-button" type="button" title="Cerrar" @click="detailItem = null">
              <X :size="20" />
            </button>
          </div>
          <dl class="prospect-detail-grid">
            <template v-if="detailItem.kind === 'recordatorio'">
              <div><dt>Estado</dt><dd><span class="badge">{{ detailItem.item.estado }}</span></dd></div>
              <div><dt>Fecha programada</dt><dd>{{ dateTime(detailItem.item.fecha_programada) }}</dd></div>
              <div v-if="detailItem.item.fecha_realizada"><dt>Realizada en</dt><dd>{{ dateTime(detailItem.item.fecha_realizada) }}</dd></div>
              <div class="full-field"><dt>Actividad</dt><dd>{{ detailItem.item.descripcion }}</dd></div>
            </template>
            <template v-else>
              <div><dt>Fecha</dt><dd>{{ dateTime(detailItem.item.fecha || detailItem.item.created_at) }}</dd></div>
              <div><dt>Usuario</dt><dd>{{ fullName(detailItem.item.usuario) }}</dd></div>
              <div class="full-field"><dt>Descripcion</dt><dd>{{ detailItem.item.descripcion }}</dd></div>
              <div class="full-field"><dt>Resultado</dt><dd>{{ detailItem.item.resultado || 'Sin resultado adicional' }}</dd></div>
            </template>
          </dl>
          <div class="form-actions">
            <button
              v-if="detailItem.kind === 'recordatorio' && detailItem.item.estado !== 'Realizada'"
              class="primary-inline"
              type="button"
              @click="completeReminder(detailItem.item)"
            >
              <CheckCircle2 :size="18" />
              Marcar realizada
            </button>
            <button class="secondary-button" type="button" @click="detailItem = null">Cerrar</button>
          </div>
        </section>
      </div>

      <div v-if="orderModalOpen" class="modal-backdrop" @click.self="orderModalOpen = false">
        <form class="modal-card order-modal-card" @submit.prevent="createOrder">
          <div class="modal-header">
            <div>
              <p class="eyebrow">Orden de pago</p>
              <h2>Crear orden para WhatsApp</h2>
              <p class="muted">Selecciona los modulos y descuentos que acordaste con el prospecto.</p>
            </div>
            <button class="top-icon-button" type="button" title="Cerrar" @click="orderModalOpen = false">
              <X :size="20" />
            </button>
          </div>
          <div class="order-modal-layout">
            <aside class="order-program-list">
              <button v-for="programa in programOptions" :key="programa.nombre" type="button" :class="{ active: selectedProgram === programa.nombre }" @click="selectedProgram = programa.nombre">
                <strong>{{ programa.nombre }}</strong>
                <small>{{ programa.modulos.length }} modulos disponibles</small>
              </button>
            </aside>
            <section class="order-selector-panel">
              <div class="order-selector-head">
                <div>
                  <p class="eyebrow">Programa seleccionado</p>
                  <h3>{{ selectedProgram || 'Selecciona un programa' }}</h3>
                </div>
                <button class="secondary-button" type="button" @click="selectFullProgram">Seleccionar todo</button>
              </div>
              <div class="order-grid">
                <label v-for="modulo in moduleOptions" :key="modulo.external_modulo_id" class="check-row module-check-row">
                  <input v-model="orderForm.modulos" type="checkbox" :value="modulo.external_modulo_id" />
                  <span><strong>{{ modulo.nombre }}</strong><small>{{ modulo.precio }} Bs</small></span>
                </label>
              </div>
              <div class="discount-section">
                <p class="eyebrow">Descuentos</p>
                <div class="order-grid">
                  <label v-for="descuento in descuentos" :key="descuento.id" class="check-row">
                    <input v-model="orderForm.descuentos" type="checkbox" :value="descuento.id" />
                    <span>{{ descuento.nombre }} - {{ descuento.porcentaje }}%</span>
                  </label>
                </div>
              </div>
            </section>
          </div>
          <div class="form-actions">
            <button type="submit" :disabled="orderForm.modulos.length === 0">
              <CreditCard :size="18" />
              Generar orden
            </button>
            <button class="secondary-button" type="button" @click="orderModalOpen = false">Cancelar</button>
          </div>
        </form>
      </div>

      <div v-if="receiptOrder" class="modal-backdrop" @click.self="receiptOrder = null">
        <form class="modal-card payment-detail-modal compact-order-modal" @submit.prevent="uploadReceipt">
          <div class="modal-header">
            <div>
              <p class="eyebrow">Detalle de orden</p>
              <h2>Orden de pago</h2>
              <p class="muted">{{ receiptOrder.items?.length || 0 }} modulo(s) - {{ money(receiptOrder.total) }}</p>
            </div>
            <button class="top-icon-button" type="button" title="Cerrar" @click="receiptOrder = null">
              <X :size="20" />
            </button>
          </div>
          <section class="payment-detail-content">
            <div class="payment-detail-main">
              <div class="order-detail-status">
                <span class="badge">{{ receiptOrder.pago?.estado || receiptOrder.estado }}</span>
                <strong v-if="receiptOrder.estado !== (receiptOrder.pago?.estado || receiptOrder.estado)">{{ receiptOrder.estado }}</strong>
              </div>
              <ul class="order-detail-modules">
                <li v-for="item in receiptOrder.items" :key="item.id">
                  {{ item.modulo_nombre }} - {{ money(item.precio) }}
                </li>
              </ul>
              <dl class="payment-total-summary">
                <div><dt>Monto total</dt><dd>{{ money(receiptOrder.subtotal) }}</dd></div>
                <div><dt>Descuento</dt><dd>{{ money(receiptOrder.descuento_total) }}</dd></div>
                <div><dt>Total a pagar</dt><dd>{{ money(receiptOrder.total) }}</dd></div>
              </dl>

              <template v-if="canUploadReceipt(receiptOrder)">
                <p class="eyebrow">Registrar pago recibido</p>
                <input type="file" accept="image/*,.pdf" required @change="handleReceipt" />
                <input v-model="receiptForm.remitente" required placeholder="Nombre del remitente" />
                <input v-model="receiptForm.hora_pago" required type="datetime-local" />
                <textarea v-model="receiptForm.observacion" placeholder="Observacion para coordinacion"></textarea>
                <button class="primary-inline" type="submit" :disabled="!receiptForm.archivo">
                  <FileCheck2 :size="18" />
                  Enviar a revision
                </button>
              </template>

              <section v-else-if="latestReceipt(receiptOrder)" class="receipt-submission-card">
                <p class="eyebrow">Comprobante registrado</p>
                <dl class="receipt-review-grid">
                  <div><dt>Estado</dt><dd>{{ latestReceipt(receiptOrder).estado_revision || receiptOrder.pago?.estado }}</dd></div>
                  <div><dt>Archivo</dt><dd>{{ latestReceipt(receiptOrder).nombre_archivo || 'Comprobante cargado' }}</dd></div>
                  <div><dt>Remitente</dt><dd>{{ latestReceipt(receiptOrder).remitente || 'Sin remitente' }}</dd></div>
                  <div><dt>Hora de pago</dt><dd>{{ dateTime(latestReceipt(receiptOrder).hora_pago) }}</dd></div>
                  <div class="full-field"><dt>Observacion</dt><dd>{{ latestReceipt(receiptOrder).observacion || receiptOrder.pago?.observacion_validacion || 'Sin observacion' }}</dd></div>
                </dl>
              </section>

              <p v-else class="muted">Esta orden no tiene pago generado todavia.</p>
            </div>
            <aside class="payment-detail-side">
              <section class="payment-qr-panel">
                <div>
                  <p class="eyebrow">QR enviado al cliente</p>
                  <strong>{{ money(receiptOrder.total) }}</strong>
                </div>
                <img :src="DEFAULT_PAYMENT_QR" alt="QR de pago" />
              </section>
              <div v-if="receiptForm.archivo && canUploadReceipt(receiptOrder)" class="receipt-preview-panel">
                <p class="eyebrow">Previsualizacion del comprobante</p>
                <img v-if="isReceiptImage()" :src="receiptForm.archivo" alt="Previsualizacion del comprobante" />
                <div v-else class="receipt-file-preview">
                  <FileText :size="28" />
                  <span>{{ receiptForm.nombre_archivo || 'Archivo seleccionado' }}</span>
                </div>
              </div>
            </aside>
          </section>
        </form>
      </div>
    </Teleport>
  </section>
</template>
