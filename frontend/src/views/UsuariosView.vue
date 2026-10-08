<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'
import { Edit3, Plus, Search, ShieldCheck, UserRound, Users, X } from '@lucide/vue'
import { changeUsuarioEstado, createUsuario, listUsuarios, updateUsuario } from '../services/api'

const usuarios = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const filters = ref({ buscar: '', rol: '', estado: '' })
const editing = ref(null)
const modalOpen = ref(false)
const form = ref(emptyForm())
const formInstance = ref(Date.now())

const title = computed(() => (editing.value ? 'Editar usuario' : 'Crear usuario'))

function emptyForm() {
  return {
    nombre: '',
    apellido: '',
    correo: '',
    telefono: '',
    password: '',
    rol: 'vendedor',
    estado: 'activo',
  }
}

function initials(usuario) {
  return `${usuario.nombre?.[0] || ''}${usuario.apellido?.[0] || ''}`.toUpperCase()
}

async function loadUsuarios() {
  loading.value = true
  error.value = ''

  try {
    usuarios.value = await listUsuarios(filters.value)
  } catch (exception) {
    error.value = exception.response?.data?.message || 'No se pudo cargar usuarios.'
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editing.value = null
  form.value = emptyForm()
  formInstance.value = Date.now()
  error.value = ''
  modalOpen.value = true
  nextTick(() => {
    form.value = emptyForm()
  })
}

function openEdit(usuario) {
  editing.value = usuario
  form.value = {
    nombre: usuario.nombre,
    apellido: usuario.apellido,
    correo: usuario.correo,
    telefono: usuario.telefono || '',
    password: '',
    rol: usuario.rol,
    estado: usuario.estado,
  }
  formInstance.value = Date.now()
  error.value = ''
  modalOpen.value = true
}

function closeModal() {
  modalOpen.value = false
  editing.value = null
  form.value = emptyForm()
}

async function save() {
  saving.value = true
  error.value = ''

  try {
    const payload = { ...form.value }
    if (editing.value && !payload.password) delete payload.password

    if (editing.value) {
      await updateUsuario(editing.value.id, payload)
    } else {
      await createUsuario(payload)
    }

    closeModal()
    await loadUsuarios()
  } catch (exception) {
    error.value = exception.response?.data?.message || exception.response?.data?.mensaje || 'No se pudo guardar.'
  } finally {
    saving.value = false
  }
}

async function toggleEstado(usuario) {
  const estado = usuario.estado === 'activo' ? 'inactivo' : 'activo'
  await changeUsuarioEstado(usuario.id, estado)
  await loadUsuarios()
}

onMounted(loadUsuarios)
</script>

<template>
  <section class="admin-page">
    <section class="admin-panel users-panel">
      <div class="admin-hero">
        <div class="admin-hero-icon">
          <Users :size="42" />
        </div>
        <div>
          <p class="eyebrow">Usuarios</p>
          <h2>Usuarios del sistema</h2>
          <p>Gestiona las cuentas de acceso, roles y estados de los usuarios del sistema.</p>
        </div>
        <button class="primary-action" type="button" @click="openCreate">
          <Plus :size="23" />
          Crear usuario
        </button>
      </div>

      <div class="users-filters">
        <label class="search-box">
          <Search :size="23" />
          <input v-model="filters.buscar" placeholder="Buscar por nombre, correo o rol..." @input="loadUsuarios" />
        </label>
        <label class="select-box">
          <UserRound :size="21" />
          <select v-model="filters.rol" @change="loadUsuarios">
            <option value="">Todos los roles</option>
            <option value="administrador">Administrador</option>
            <option value="coordinador">Coordinador</option>
            <option value="vendedor">Vendedor</option>
          </select>
        </label>
        <label class="select-box">
          <ShieldCheck :size="21" />
          <select v-model="filters.estado" @change="loadUsuarios">
            <option value="">Todos los estados</option>
            <option value="activo">Activo</option>
            <option value="inactivo">Inactivo</option>
          </select>
        </label>
      </div>

      <p v-if="error && !modalOpen" class="error-message">{{ error }}</p>
      <div v-if="loading" class="muted">Cargando usuarios...</div>

      <div v-else class="users-table">
        <table>
          <thead>
            <tr>
              <th>Nombre</th>
              <th>Correo</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Ultimo acceso</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="usuario in usuarios" :key="usuario.id">
              <td>
                <div class="identity-cell">
                  <div class="avatar-badge">{{ initials(usuario) }}</div>
                  <div>
                    <strong>{{ usuario.nombre }} {{ usuario.apellido }}</strong>
                    <small>{{ usuario.rol === 'administrador' ? 'Administrador del sistema' : usuario.rol }}</small>
                  </div>
                </div>
              </td>
              <td>{{ usuario.correo }}</td>
              <td><span class="role-pill">{{ usuario.rol }}</span></td>
              <td><span class="status-pill" :class="usuario.estado"><span></span>{{ usuario.estado }}</span></td>
              <td>{{ usuario.updated_at ? new Date(usuario.updated_at).toLocaleDateString() : 'Sin acceso' }}</td>
              <td>
                <div class="user-actions">
                  <button class="edit-action" type="button" title="Editar" @click="openEdit(usuario)">
                    <Edit3 :size="20" />
                  </button>
                  <button class="state-action" :class="{ activate: usuario.estado !== 'activo' }" type="button" @click="toggleEstado(usuario)">
                    {{ usuario.estado === 'activo' ? 'Desactivar' : 'Activar' }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="users-summary">
        Mostrando 1 a {{ usuarios.length }} de {{ usuarios.length }} usuarios
      </div>
    </section>

    <Teleport to="body">
      <div v-if="modalOpen" class="modal-backdrop" @click.self="closeModal">
        <form :key="formInstance" class="modal-card" autocomplete="off" @submit.prevent="save">
          <div class="autofill-guard" aria-hidden="true">
            <input :name="`guard-user-${formInstance}`" type="text" tabindex="-1" autocomplete="username" />
            <input :name="`guard-pass-${formInstance}`" type="password" tabindex="-1" autocomplete="current-password" />
          </div>
          <div class="modal-header">
            <div>
              <p class="eyebrow">Usuarios</p>
              <h2>{{ title }}</h2>
            </div>
            <button class="top-icon-button" type="button" title="Cerrar" @click="closeModal">
              <X :size="20" />
            </button>
          </div>

          <div class="form-grid">
            <label>Nombre<input v-model="form.nombre" :name="`usuario-nombre-${formInstance}`" autocomplete="off" required /></label>
            <label>Apellido<input v-model="form.apellido" :name="`usuario-apellido-${formInstance}`" autocomplete="off" required /></label>
            <label>Correo<input v-model="form.correo" :name="`usuario-correo-${formInstance}`" type="email" autocomplete="off" required /></label>
            <label>Telefono<input v-model="form.telefono" :name="`usuario-telefono-${formInstance}`" type="tel" autocomplete="off" /></label>
            <label>
              Rol
              <select v-model="form.rol" :name="`usuario-rol-${formInstance}`" autocomplete="off" required>
                <option value="administrador">Administrador</option>
                <option value="coordinador">Coordinador</option>
                <option value="vendedor">Vendedor</option>
              </select>
            </label>
            <label>
              Estado
              <select v-model="form.estado" :name="`usuario-estado-${formInstance}`" autocomplete="off" required>
                <option value="activo">Activo</option>
                <option value="inactivo">Inactivo</option>
              </select>
            </label>
            <label class="full-field">
              Contrasena
              <input v-model="form.password" :name="`usuario-clave-${formInstance}`" type="password" autocomplete="new-password" :required="!editing" minlength="8" />
            </label>
          </div>

          <p v-if="error" class="error-message">{{ error }}</p>
          <div class="form-actions">
            <button type="submit" :disabled="saving">{{ saving ? 'Guardando...' : 'Guardar' }}</button>
            <button class="secondary-button" type="button" @click="closeModal">Cancelar</button>
          </div>
        </form>
      </div>
    </Teleport>
  </section>
</template>
