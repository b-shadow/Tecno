<script setup>
import { computed, onMounted, ref } from 'vue'
import { Eye, FileUp, RefreshCw, Upload, X } from '@lucide/vue'
import { importarProspectos, listProspectos } from '../services/api'
import { authState } from '../services/auth'

const estados = ['Nuevo', 'Contactado', 'Interesado', 'En proceso', 'Convertido', 'Perdido']
const requiredColumns = ['nombres', 'apellidos', 'ci', 'telefono', 'profesion', 'ubicacion', 'correo']
const prospectos = ref([])
const filters = ref({ buscar: '', estado: '' })
const error = ref('')
const message = ref('')
const importModalOpen = ref(false)
const importFile = ref(null)
const importFileKey = ref(Date.now())
const importErrors = ref([])
const importing = ref(false)
const selectedProspect = ref(null)

const canImport = computed(() => ['administrador', 'coordinador'].includes(authState.usuario?.rol))

async function load() {
  error.value = ''
  try {
    prospectos.value = await listProspectos(filters.value)
  } catch (exception) {
    error.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudieron cargar prospectos.'
  }
}

function openImportModal() {
  importModalOpen.value = true
  importFile.value = null
  importErrors.value = []
  message.value = ''
  importFileKey.value = Date.now()
}

function closeImportModal() {
  importModalOpen.value = false
  importFile.value = null
  importErrors.value = []
}

function handleImportFile(event) {
  importFile.value = event.target.files[0] || null
  importErrors.value = []
}

function clearImportFile() {
  importFile.value = null
  importFileKey.value = Date.now()
  importErrors.value = []
}

function openInterests(prospecto) {
  selectedProspect.value = prospecto
}

function closeInterests() {
  selectedProspect.value = null
}

async function readFileAsText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result || ''))
    reader.onerror = () => reject(reader.error)
    reader.readAsText(file)
  })
}

async function importCsv() {
  if (!importFile.value) return

  importing.value = true
  error.value = ''
  message.value = ''
  importErrors.value = []

  try {
    const csv = await readFileAsText(importFile.value)
    const result = await importarProspectos({ csv })
    message.value = `${result.creados} prospecto(s) cargado(s) correctamente.`
    closeImportModal()
    await load()
  } catch (exception) {
    const data = exception.response?.data
    importErrors.value = data?.errores || [{ error: data?.mensaje || 'No se pudo importar el archivo.' }]
  } finally {
    importing.value = false
  }
}

function sellerForInterest(prospecto, interes) {
  return interes.vendedor ? `${interes.vendedor.nombre} ${interes.vendedor.apellido}` : 'Sin vendedor'
}

onMounted(load)
</script>

<template>
  <section class="public-board">
    <section class="table-surface">
      <div class="table-header">
        <div>
          <p class="eyebrow">Prospectos</p>
          <h2>Cartera comercial</h2>
          <p>Los prospectos se cargan masivamente desde archivos CSV validados.</p>
        </div>
        <div class="header-actions">
          <button v-if="canImport" class="primary-inline" type="button" @click="openImportModal">
            <FileUp :size="18" />
            Cargar CSV
          </button>
          <button class="secondary-button" type="button" @click="load">
            <RefreshCw :size="17" />
            Actualizar
          </button>
        </div>
      </div>

      <div class="filters">
        <input v-model="filters.buscar" placeholder="Buscar prospecto" @input="load" />
        <select v-model="filters.estado" @change="load">
          <option value="">Todos</option>
          <option v-for="estado in estados" :key="estado" :value="estado">{{ estado }}</option>
        </select>
      </div>

      <p v-if="message" class="success-message">{{ message }}</p>
      <p v-if="error" class="error-message">{{ error }}</p>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Prospecto</th>
              <th>Contacto</th>
              <th>Perfil</th>
              <th>Estado</th>
              <th>Intereses</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="prospecto in prospectos" :key="prospecto.id">
              <td>{{ prospecto.nombre }} {{ prospecto.apellido }}<br><small>{{ prospecto.documento }}</small></td>
              <td>{{ prospecto.correo }}<br><small>{{ prospecto.telefono }}</small></td>
              <td>{{ prospecto.profesion || 'Sin profesion' }}<br><small>{{ prospecto.ubicacion || 'Sin ubicacion' }}</small></td>
              <td><span class="badge">{{ prospecto.estado }}</span></td>
              <td>
                <button
                  v-if="prospecto.intereses?.length"
                  class="secondary-button compact-button"
                  type="button"
                  @click="openInterests(prospecto)"
                >
                  <Eye :size="17" />
                  Ver intereses ({{ prospecto.intereses.length }})
                </button>
                <span v-else>Sin intereses registrados</span>
              </td>
            </tr>
            <tr v-if="prospectos.length === 0">
              <td colspan="5">No hay prospectos registrados.</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <Teleport to="body">
      <div v-if="selectedProspect" class="modal-backdrop" @click.self="closeInterests">
        <section class="modal-card prospect-interests-modal">
          <div class="modal-header">
            <div>
              <p class="eyebrow">Intereses registrados</p>
              <h2>{{ selectedProspect.nombre }} {{ selectedProspect.apellido }}</h2>
              <p class="muted">{{ selectedProspect.correo }} · {{ selectedProspect.telefono }}</p>
            </div>
            <button class="top-icon-button" type="button" title="Cerrar" @click="closeInterests">
              <X :size="20" />
            </button>
          </div>

          <dl class="prospect-detail-grid">
            <div>
              <dt>Documento</dt>
              <dd>{{ selectedProspect.documento }}</dd>
            </div>
            <div>
              <dt>Estado</dt>
              <dd><span class="badge">{{ selectedProspect.estado }}</span></dd>
            </div>
            <div>
              <dt>Profesion</dt>
              <dd>{{ selectedProspect.profesion || 'Sin profesion' }}</dd>
            </div>
            <div>
              <dt>Ubicacion</dt>
              <dd>{{ selectedProspect.ubicacion || 'Sin ubicacion' }}</dd>
            </div>
          </dl>

          <div class="prospect-interest-list modal-interest-list">
            <article v-for="interes in selectedProspect.intereses" :key="interes.id">
              <div>
                <strong>{{ interes.modulo_nombre }}</strong>
                <span>{{ interes.programa_nombre }}</span>
              </div>
              <small>{{ sellerForInterest(selectedProspect, interes) }}</small>
            </article>
          </div>
        </section>
      </div>
    </Teleport>

    <Teleport to="body">
      <div v-if="importModalOpen" class="modal-backdrop" @click.self="closeImportModal">
        <form class="modal-card import-modal-card" @submit.prevent="importCsv">
          <div class="modal-header">
            <div>
              <p class="eyebrow">Importacion CSV</p>
              <h2>Cargar prospectos</h2>
              <p class="muted">El archivo debe contener las columnas requeridas y todos los campos completos.</p>
            </div>
            <button class="top-icon-button" type="button" title="Cerrar" @click="closeImportModal">
              <X :size="20" />
            </button>
          </div>

          <section class="required-columns">
            <span v-for="column in requiredColumns" :key="column">{{ column }}</span>
          </section>

          <label class="csv-upload-box">
            <Upload :size="28" />
            <strong>{{ importFile?.name || 'Selecciona un archivo CSV' }}</strong>
            <small>Solo se cargara si el archivo contiene las columnas requeridas.</small>
            <input :key="importFileKey" type="file" accept=".csv,text/csv" required @change="handleImportFile" />
          </label>

          <div v-if="importFile" class="form-actions">
            <button class="secondary-button" type="button" @click="clearImportFile">Limpiar archivo</button>
          </div>

          <section v-if="importErrors.length" class="error-message import-errors">
            <strong>Corrige el CSV antes de cargarlo:</strong>
            <ul>
              <li v-for="(item, index) in importErrors" :key="index">
                <span v-if="item.fila">Fila {{ item.fila }}: </span>
                <span v-if="item.columna">({{ item.columna }}) </span>
                {{ item.error }}
              </li>
            </ul>
          </section>

          <div class="form-actions">
            <button type="submit" :disabled="!importFile || importing">{{ importing ? 'Validando...' : 'Validar y cargar' }}</button>
            <button class="secondary-button" type="button" @click="closeImportModal">Cancelar</button>
          </div>
        </form>
      </div>
    </Teleport>
  </section>
</template>
