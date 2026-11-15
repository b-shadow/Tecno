<script setup>
import { computed, onMounted, ref } from 'vue'
import { RefreshCw, Search, Shuffle, UserCheck } from '@lucide/vue'
import { asignarInteres, distribuirIntereses, listIntereses, listUsuarios } from '../services/api'

const intereses = ref([])
const vendedores = ref([])
const loading = ref(true)
const distributing = ref(false)
const savingId = ref(null)
const error = ref('')
const message = ref('')
const searchTerm = ref('')
const bandeja = ref('sin-asignar')
// Vendedor elegido en cada fila antes de confirmar la asignacion.
const pending = ref({})

const sinAsignar = computed(() => intereses.value.filter((item) => !item.vendedor_id).length)
const visibleIntereses = computed(() => {
  const term = searchTerm.value.trim().toLowerCase()
  const base = intereses.value.filter((item) => {
    if (bandeja.value === 'sin-asignar') return !item.vendedor_id
    if (bandeja.value === 'asignados') return item.vendedor_id
    return true
  })

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
    const [interestData, sellerData] = await Promise.all([
      listIntereses(),
      listUsuarios({ rol: 'vendedor', estado: 'activo' }),
    ])
    intereses.value = interestData
    vendedores.value = sellerData
    pending.value = Object.fromEntries(interestData.map((item) => [item.id, item.vendedor_id || '']))
  } catch (exception) {
    error.value = errorText(exception, 'No se pudo cargar interesados.')
  } finally {
    loading.value = false
  }
}

async function assign(interes) {
  const vendedorId = pending.value[interes.id]
  if (!vendedorId || vendedorId === interes.vendedor_id) return

  savingId.value = interes.id
  error.value = ''
  message.value = ''
  try {
    const updated = await asignarInteres(interes.id, vendedorId)
    message.value = interes.vendedor_id
      ? `${fullName(updated.prospecto)} pasa a ${fullName(updated.vendedor)} con todo su historial.`
      : `${fullName(updated.prospecto)} asignado a ${fullName(updated.vendedor)}.`
    await load()
  } catch (exception) {
    error.value = errorText(exception, 'No se pudo asignar el interesado.')
  } finally {
    savingId.value = null
  }
}

async function distribute() {
  distributing.value = true
  error.value = ''
  message.value = ''
  try {
    const result = await distribuirIntereses()
    message.value = `${result.asignados} interes(es) repartidos entre ${vendedores.value.length} vendedor(es) segun su carga actual.`
    await load()
  } catch (exception) {
    error.value = errorText(exception, 'No se pudo distribuir.')
  } finally {
    distributing.value = false
  }
}

function errorText(exception, fallback) {
  return exception.response?.data?.mensaje || exception.response?.data?.message || fallback
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
          <h2>Asignacion de interesados</h2>
          <p>Asigna cada interesado a un vendedor o repartelos de forma equitativa. Al reasignar, el nuevo vendedor recibe todo el historial.</p>
        </div>
        <div class="header-actions">
          <button
            class="primary-inline"
            type="button"
            :disabled="distributing || !sinAsignar || !vendedores.length"
            @click="distribute"
          >
            <Shuffle :size="18" />
            {{ distributing ? 'Repartiendo...' : `Repartir ${sinAsignar} pendientes` }}
          </button>
          <button class="secondary-button" type="button" @click="load">
            <RefreshCw :size="17" />
            Actualizar
          </button>
        </div>
      </div>

      <div class="filters interested-filters">
        <label>
          Buscar
          <span class="input-with-icon">
            <Search :size="19" />
            <input v-model="searchTerm" placeholder="Nombre, correo, telefono, programa, modulo o vendedor..." />
          </span>
        </label>
        <label>
          Mostrar
          <select v-model="bandeja">
            <option value="sin-asignar">Sin asignar</option>
            <option value="asignados">Asignados</option>
            <option value="todos">Todos</option>
          </select>
        </label>
      </div>

      <p v-if="message" class="success-message" role="status">{{ message }}</p>
      <p v-if="error" class="error-message" role="alert">{{ error }}</p>
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
              <th>Vendedor</th>
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
                  <select v-model="pending[interes.id]" :aria-label="`Vendedor para ${fullName(interes.prospecto)}`">
                    <option value="" disabled>Sin vendedor</option>
                    <option v-for="vendedor in vendedores" :key="vendedor.id" :value="vendedor.id">{{ fullName(vendedor) }}</option>
                  </select>
                  <button
                    class="secondary-button compact-button"
                    type="button"
                    :disabled="savingId === interes.id || !pending[interes.id] || pending[interes.id] === interes.vendedor_id"
                    @click="assign(interes)"
                  >
                    <UserCheck :size="16" />
                    {{ interes.vendedor_id ? 'Reasignar' : 'Asignar' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <p v-if="!loading && visibleIntereses.length === 0" class="muted">
        {{ bandeja === 'sin-asignar' ? 'No hay interesados pendientes de asignar.' : 'No hay interesados para mostrar.' }}
      </p>
    </section>
  </section>
</template>
