<script setup>
import { computed, onMounted, ref } from 'vue'
import { RefreshCw, Search, UserCheck } from '@lucide/vue'
import { useRouter } from 'vue-router'
import { listIntereses, tomarInteres } from '../services/api'
import { authState } from '../services/auth'

const router = useRouter()
const intereses = ref([])
const loading = ref(true)
const error = ref('')
const message = ref('')
const searchTerm = ref('')

const visibleIntereses = computed(() => {
  const term = searchTerm.value.trim().toLowerCase()
  const base = intereses.value.filter((item) => !item.vendedor_id)

  if (!term) return base

  return base.filter((item) => [
    fullName(item.prospecto),
    item.prospecto?.correo,
    item.prospecto?.telefono,
    item.programa_nombre,
    item.modulo_nombre,
    item.estado,
    item.vendedor ? fullName(item.vendedor) : 'Sin vendedor',
  ].some((value) => String(value || '').toLowerCase().includes(term)))
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    intereses.value = await listIntereses()
  } catch (exception) {
    error.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudo cargar interesados.'
  } finally {
    loading.value = false
  }
}

async function takeInterest(interes) {
  error.value = ''
  message.value = ''
  try {
    const updated = await tomarInteres(interes.id)
    intereses.value = intereses.value.map((item) => (item.id === updated.id ? updated : item))
    message.value = 'Seguimiento tomado correctamente.'
    router.push({ name: 'agenda', query: { interes: updated.id } })
  } catch (exception) {
    error.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudo tomar el seguimiento.'
  }
}

function fullName(person) {
  return [person?.nombre, person?.apellido].filter(Boolean).join(' ') || 'Sin nombre'
}

function dateTime(value) {
  return value ? new Date(value).toLocaleString('es-BO') : 'Sin fecha'
}

onMounted(load)
</script>

<template>
  <section class="public-board">
    <section class="table-surface">
      <div class="table-header">
        <div>
          <p class="eyebrow">Interesados</p>
          <h2>Listado de interesados</h2>
          <p>Consulta los intereses nuevos que todavia no fueron tomados por un vendedor.</p>
        </div>
        <button class="secondary-button" type="button" @click="load">
          <RefreshCw :size="17" />
          Actualizar
        </button>
      </div>

      <div class="filters interested-filters">
        <label>
          Buscar
          <span class="input-with-icon">
            <Search :size="19" />
            <input v-model="searchTerm" placeholder="Nombre, correo, telefono, programa o modulo..." />
          </span>
        </label>
      </div>

      <p v-if="message" class="success-message">{{ message }}</p>
      <p v-if="error" class="error-message">{{ error }}</p>
      <p v-if="loading" class="muted">Cargando interesados...</p>

      <div class="responsive-table">
        <table>
          <thead>
            <tr>
              <th>Interesado</th>
              <th>Contacto</th>
              <th>Interes</th>
              <th>Estado</th>
              <th>Ultima actividad</th>
              <th>Accion</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="interes in visibleIntereses" :key="interes.id">
              <td>
                <strong>{{ fullName(interes.prospecto) }}</strong>
                <small>{{ interes.prospecto?.documento || 'Sin CI' }}</small>
              </td>
              <td>
                <span>{{ interes.prospecto?.correo || 'Sin correo' }}</span>
                <small>{{ interes.prospecto?.telefono || 'Sin telefono' }}</small>
              </td>
              <td>
                <strong>{{ interes.modulo_nombre }}</strong>
                <small>{{ interes.programa_nombre }}</small>
              </td>
              <td><span class="badge">{{ interes.estado }}</span></td>
              <td>{{ dateTime(interes.ultima_actividad_en || interes.created_at) }}</td>
              <td>
                <div class="table-actions">
                  <button v-if="authState.usuario?.rol === 'vendedor' && !interes.vendedor_id" class="secondary-button compact-button" type="button" @click="takeInterest(interes)">
                    <UserCheck :size="16" />
                    Tomar
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <p v-if="!loading && visibleIntereses.length === 0" class="muted">No hay interesados para mostrar.</p>
    </section>
  </section>
</template>
