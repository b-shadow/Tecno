<script setup>
import { computed, onMounted, ref } from 'vue'
import { CalendarDays, CheckCircle2, ChevronLeft, ChevronRight, RefreshCw, X } from '@lucide/vue'
import { completarRecordatorio, listRecordatorios } from '../services/api'

const recordatorios = ref([])
const loading = ref(true)
const error = ref('')
const currentMonth = ref(new Date())
const selectedDate = ref(null)
const selectedActivity = ref(null)

const monthLabel = computed(() => currentMonth.value.toLocaleDateString('es-BO', { month: 'long', year: 'numeric' }))
const calendarDays = computed(() => buildCalendar(currentMonth.value))
const selectedDayActivities = computed(() => selectedDate.value ? activitiesForDay(selectedDate.value) : [])
const upcomingActivities = computed(() => [...recordatorios.value]
  .filter((item) => ['Pendiente', 'Atrasada'].includes(item.estado))
  .sort((a, b) => new Date(a.fecha_programada) - new Date(b.fecha_programada))
  .slice(0, 6))

async function load() {
  loading.value = true
  error.value = ''
  try {
    recordatorios.value = await listRecordatorios()
  } catch (exception) {
    error.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudo cargar tu agenda.'
  } finally {
    loading.value = false
  }
}

function buildCalendar(date) {
  const year = date.getFullYear()
  const month = date.getMonth()
  const first = new Date(year, month, 1)
  const start = new Date(first)
  start.setDate(first.getDate() - ((first.getDay() + 6) % 7))

  return Array.from({ length: 42 }, (_, index) => {
    const day = new Date(start)
    day.setDate(start.getDate() + index)
    const key = dayKey(day)
    const activities = activitiesForDay(key)

    return {
      date: day,
      key,
      inMonth: day.getMonth() === month,
      today: key === dayKey(new Date()),
      activities,
    }
  })
}

function activitiesForDay(dateKey) {
  return recordatorios.value.filter((item) => dayKey(new Date(item.fecha_programada)) === dateKey)
}

function dayKey(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  return `${year}-${month}-${day}`
}

function changeMonth(offset) {
  const next = new Date(currentMonth.value)
  next.setMonth(next.getMonth() + offset)
  currentMonth.value = next
}

function openDay(day) {
  selectedDate.value = day.key
  selectedActivity.value = null
}

function openActivity(activity) {
  selectedActivity.value = activity
}

function openActivityFromUpcoming(activity) {
  selectedDate.value = dayKey(new Date(activity.fecha_programada))
  selectedActivity.value = activity
}

function closeModals() {
  selectedDate.value = null
  selectedActivity.value = null
}

function backToDay() {
  selectedActivity.value = null
}

async function markDone(activity) {
  await completarRecordatorio(activity.id)
  await load()
  const updated = recordatorios.value.find((item) => item.id === activity.id)
  selectedActivity.value = updated || null
}

function fullName(person) {
  return [person?.nombre, person?.apellido].filter(Boolean).join(' ') || 'Sin prospecto'
}

function formatTime(value) {
  return new Date(value).toLocaleTimeString('es-BO', { hour: '2-digit', minute: '2-digit' })
}

function formatDate(value) {
  return new Date(value).toLocaleDateString('es-BO', { weekday: 'long', day: 'numeric', month: 'long' })
}

function formatDateTime(value) {
  return new Date(value).toLocaleString('es-BO', {
    day: 'numeric',
    month: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(load)
</script>

<template>
  <section class="public-board seller-home">
    <section class="seller-home-grid">
      <article class="table-surface seller-calendar-card">
        <div class="table-header seller-calendar-heading">
          <div>
            <h2>Calendario de actividades</h2>
          </div>
          <button class="secondary-button" type="button" @click="load">
            <RefreshCw :size="17" />
            Actualizar
          </button>
        </div>
        <p v-if="error" class="error-message">{{ error }}</p>
        <div class="calendar-toolbar">
          <button class="icon-button" type="button" @click="changeMonth(-1)"><ChevronLeft :size="19" /></button>
          <h3>{{ monthLabel }}</h3>
          <button class="icon-button" type="button" @click="changeMonth(1)"><ChevronRight :size="19" /></button>
        </div>
        <div class="calendar-weekdays">
          <span>Lun</span><span>Mar</span><span>Mie</span><span>Jue</span><span>Vie</span><span>Sab</span><span>Dom</span>
        </div>
        <div class="seller-calendar">
          <button
            v-for="day in calendarDays"
            :key="day.key"
            type="button"
            class="calendar-day"
            :class="{ muted: !day.inMonth, today: day.today, hasItems: day.activities.length }"
            @click="openDay(day)"
          >
            <strong>{{ day.date.getDate() }}</strong>
            <span v-if="day.activities.length">{{ day.activities.length }}</span>
          </button>
        </div>
      </article>

      <aside class="table-surface upcoming-card">
        <div class="table-header compact-header">
          <div>
            <p class="eyebrow">Proximos contactos</p>
            <h3>Actividades pendientes</h3>
          </div>
        </div>
        <button v-for="activity in upcomingActivities" :key="activity.id" type="button" class="activity-list-row" @click="openActivityFromUpcoming(activity)">
          <span class="badge" :class="{ danger: activity.estado === 'Atrasada', warning: activity.estado === 'Pendiente' }">{{ activity.estado }}</span>
          <strong>{{ fullName(activity.prospecto) }}</strong>
          <small>{{ formatDate(activity.fecha_programada) }} - {{ formatTime(activity.fecha_programada) }}</small>
          <em>{{ activity.descripcion }}</em>
        </button>
        <p v-if="!loading && upcomingActivities.length === 0" class="muted">No tienes actividades pendientes.</p>
      </aside>
    </section>

    <Teleport to="body">
      <div v-if="selectedDate" class="modal-backdrop" @click.self="closeModals">
        <section class="modal-card seller-day-modal">
          <template v-if="!selectedActivity">
            <div class="modal-header">
              <div>
                <p class="eyebrow">Actividades del dia</p>
                <h2>{{ formatDate(`${selectedDate}T12:00:00`) }}</h2>
              </div>
              <button class="top-icon-button" type="button" @click="closeModals"><X :size="20" /></button>
            </div>
            <div class="day-activity-list">
              <button v-for="activity in selectedDayActivities" :key="activity.id" type="button" class="activity-list-row" @click="openActivity(activity)">
                <span class="badge" :class="{ danger: activity.estado === 'Atrasada', success: activity.estado === 'Realizada', warning: activity.estado === 'Pendiente' }">{{ activity.estado }}</span>
                <strong>{{ fullName(activity.prospecto) }}</strong>
                <small>{{ formatTime(activity.fecha_programada) }} - {{ activity.interes?.modulo_nombre || 'Sin modulo' }}</small>
                <em>{{ activity.descripcion }}</em>
              </button>
              <p v-if="selectedDayActivities.length === 0" class="muted">No hay actividades para este dia.</p>
            </div>
          </template>

          <template v-else>
            <div class="modal-header">
              <div>
                <p class="eyebrow">Detalle de actividad</p>
                <h2>{{ fullName(selectedActivity.prospecto) }}</h2>
              </div>
              <button class="top-icon-button" type="button" @click="closeModals"><X :size="20" /></button>
            </div>
            <dl class="prospect-detail-grid">
              <div><dt>Estado</dt><dd><span class="badge">{{ selectedActivity.estado }}</span></dd></div>
              <div><dt>Fecha y hora</dt><dd>{{ formatDate(selectedActivity.fecha_programada) }} - {{ formatTime(selectedActivity.fecha_programada) }}</dd></div>
              <div><dt>Modulo</dt><dd>{{ selectedActivity.interes?.modulo_nombre || 'Sin modulo' }}</dd></div>
              <div><dt>Telefono</dt><dd>{{ selectedActivity.prospecto?.telefono || 'Sin telefono' }}</dd></div>
              <div class="full-field"><dt>Descripcion</dt><dd>{{ selectedActivity.descripcion }}</dd></div>
              <div v-if="selectedActivity.fecha_realizada"><dt>Marcada como realizada</dt><dd>{{ formatDateTime(selectedActivity.fecha_realizada) }}</dd></div>
            </dl>
            <div class="form-actions">
              <button class="secondary-button" type="button" @click="backToDay">
                <CalendarDays :size="18" />
                Volver al dia
              </button>
              <button v-if="selectedActivity.estado !== 'Realizada'" class="primary-inline" type="button" @click="markDone(selectedActivity)">
                <CheckCircle2 :size="18" />
                Marcar realizada
              </button>
            </div>
          </template>
        </section>
      </div>
    </Teleport>
  </section>
</template>
