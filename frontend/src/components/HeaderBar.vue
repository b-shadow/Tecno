<script setup>
import { computed, ref } from 'vue'
import { ArrowLeft, Bell, ChevronDown, EyeOff, GraduationCap, Info, KeyRound, Lock, LogIn, LogOut, Mail, Moon, Save, ShieldCheck, Sun, UserRound, X, Phone } from '@lucide/vue'
import { useRoute, useRouter } from 'vue-router'
import { authState, changePassword, logout, updateProfile } from '../services/auth'

const props = defineProps({
  internal: { type: Boolean, default: false },
  sidebarCollapsed: { type: Boolean, default: false },
  theme: { type: String, default: 'light' },
})

defineEmits(['toggle-sidebar', 'toggle-theme'])

const router = useRouter()
const route = useRoute()
const profileMenuOpen = ref(false)
const profileModalOpen = ref(false)
const logoutModalOpen = ref(false)
const profileError = ref('')
const profileMessage = ref('')
const passwordError = ref('')
const passwordMessage = ref('')
const profileForm = ref(emptyProfileForm())
const passwordForm = ref(emptyPasswordForm())

const pageTitle = computed(() => {
  const titles = {
    '/dashboard': 'Dashboard',
    '/inicio-vendedor': 'Inicio',
    '/usuarios': 'Usuarios',
    '/programas': 'Programas',
    '/modulos': 'Modulos',
    '/gestion-anuncios': 'Anuncios',
    '/pagos': 'Pagos',
    '/prospectos': 'Prospectos',
    '/validacion-pagos': 'Validacion pagos',
    '/alumnos': 'Alumnos e integracion',
    '/seguimiento': 'Ventas y comisiones',
    '/interesados': 'Interesados',
    '/agenda': 'Agenda',
    '/chats': 'Agenda',
    '/reportes': 'Reportes',
    '/notificaciones': 'Notificaciones',
    '/comisiones': 'Ventas y comisiones',
    '/exportaciones': 'Alumnos e integracion',
    '/login': 'Iniciar sesion',
  }

  return titles[route.path] || (authState.usuario ? (authState.usuario.rol === 'vendedor' ? 'Inicio' : 'Dashboard') : 'Modulos disponibles')
})

const pageSubtitle = computed(() => {
  const subtitles = {
    '/programas': 'Administra los programas academicos de la plataforma.',
    '/modulos': 'Gestiona los modulos de cada programa academico.',
    '/gestion-anuncios': 'Explora los modulos disponibles y registra nuevos intereses.',
    '/inicio-vendedor': 'Consulta tu calendario de actividades comerciales.',
    '/agenda': 'Registra el seguimiento comercial por interes del cliente.',
    '/interesados': 'Lista los interesados recibidos y abre su seguimiento.',
    '/pagos': 'Consulta el estado de tus pagos realizados.',
    '/alumnos': 'Consulta alumnos inscritos y prepara el envio al sistema academico.',
  }

  return subtitles[route.path] || ''
})

const initials = computed(() => {
  const nombre = authState.usuario?.nombre || ''
  const apellido = authState.usuario?.apellido || ''
  return `${nombre[0] || ''}${apellido[0] || ''}`.toUpperCase() || 'U'
})

function goBack() {
  const backEvent = new CustomEvent('crm:go-back', {
    detail: { handled: false },
  })
  window.dispatchEvent(backEvent)

  if (backEvent.detail.handled) {
    return
  }

  if (route.name === 'login') {
    router.push('/anuncios')
    return
  }

  if (window.history.length > 1) {
    router.back()
    return
  }

  router.push(authState.usuario ? (authState.usuario.rol === 'vendedor' ? '/inicio-vendedor' : '/dashboard') : '/anuncios')
}

function emptyProfileForm() {
  return {
    nombre: authState.usuario?.nombre || '',
    apellido: authState.usuario?.apellido || '',
    correo: authState.usuario?.correo || '',
    telefono: authState.usuario?.telefono || '',
    rol: authState.usuario?.rol || '',
  }
}

function emptyPasswordForm() {
  return {
    password_actual: '',
    password: '',
    password_confirmation: '',
  }
}

function openProfileModal() {
  profileMenuOpen.value = false
  profileError.value = ''
  profileMessage.value = ''
  passwordError.value = ''
  passwordMessage.value = ''
  profileForm.value = emptyProfileForm()
  passwordForm.value = emptyPasswordForm()
  profileModalOpen.value = true
}

function openLogoutModal() {
  profileMenuOpen.value = false
  logoutModalOpen.value = true
}

async function saveProfile() {
  profileError.value = ''
  profileMessage.value = ''
  try {
    await updateProfile({
      nombre: profileForm.value.nombre,
      apellido: profileForm.value.apellido,
      telefono: profileForm.value.telefono,
    })
    profileForm.value = emptyProfileForm()
    profileMessage.value = 'Perfil actualizado correctamente.'
  } catch (exception) {
    profileError.value = exception.response?.data?.message || 'No se pudo actualizar el perfil.'
  }
}

async function savePassword() {
  passwordError.value = ''
  passwordMessage.value = ''
  if (passwordForm.value.password !== passwordForm.value.password_confirmation) {
    passwordError.value = 'La confirmacion no coincide con la nueva contrasena.'
    return
  }

  try {
    await changePassword({ ...passwordForm.value })
    passwordForm.value = emptyPasswordForm()
    passwordMessage.value = 'Contrasena actualizada correctamente.'
  } catch (exception) {
    passwordError.value = exception.response?.data?.mensaje || exception.response?.data?.message || 'No se pudo cambiar la contrasena.'
  }
}

async function closeSession() {
  await logout()
  logoutModalOpen.value = false
  router.push('/anuncios')
}
</script>

<template>
  <header class="header-bar">
    <div class="header-title-row">
      <button class="top-icon-button" type="button" title="Volver" @click="goBack">
        <ArrowLeft :size="18" />
      </button>
      <div>
        <p class="eyebrow">{{ internal ? 'Sistema CRM Comercial Educativo' : (route.path === '/login' ? 'Acceso interno NEXO' : 'Anuncios academicos') }}</p>
        <h1>{{ pageTitle }}</h1>
        <p v-if="pageSubtitle" class="header-subtitle">{{ pageSubtitle }}</p>
      </div>
    </div>
    <div class="header-actions">
      <button v-if="internal" class="theme-switch" type="button" :title="theme === 'dark' ? 'Modo claro' : 'Modo oscuro'" @click="$emit('toggle-theme')">
        <span class="theme-icon sun"><Sun :size="17" /></span>
        <span class="theme-thumb" :class="{ dark: theme === 'dark' }"></span>
        <span class="theme-icon moon"><Moon :size="17" /></span>
      </button>
      <button v-else class="top-icon-button" type="button" :title="theme === 'dark' ? 'Modo claro' : 'Modo oscuro'" @click="$emit('toggle-theme')">
        <Sun v-if="theme === 'dark'" :size="18" />
        <Moon v-else :size="18" />
      </button>
      <template v-if="authState.usuario">
        <button class="notification-button" type="button" title="Notificaciones">
          <Bell :size="21" />
          <span></span>
        </button>
        <div class="profile-menu-wrap">
          <button class="profile-chip" type="button" @click="profileMenuOpen = !profileMenuOpen">
            <div class="profile-avatar">{{ initials }}</div>
            <div>
              <strong>{{ authState.usuario.nombre }}</strong>
              <small>{{ authState.usuario.apellido }}</small>
            </div>
            <ChevronDown :size="17" />
          </button>
          <div v-if="profileMenuOpen" class="profile-menu">
            <button type="button" @click="openProfileModal">
              <UserRound :size="17" />
              Mi perfil
            </button>
            <button type="button" @click="openLogoutModal">
              <LogOut :size="17" />
              Cerrar sesion
            </button>
          </div>
        </div>
      </template>
      <RouterLink v-else class="ghost-button" :to="route.path === '/login' ? '/anuncios' : '/login'">
        <GraduationCap v-if="route.path === '/login'" :size="18" />
        <LogIn v-else :size="18" />
        {{ route.path === '/login' ? 'Ver cursos' : 'Iniciar sesion' }}
      </RouterLink>
    </div>

    <Teleport to="body">
      <div v-if="profileModalOpen" class="modal-backdrop" @click.self="profileModalOpen = false">
        <section class="profile-card">
          <div class="profile-modal-header">
            <div class="profile-modal-icon">
              <UserRound :size="42" />
            </div>
            <div class="profile-modal-title">
              <p class="eyebrow">Mi perfil</p>
              <h2>Datos de usuario</h2>
              <p>Actualiza tu informacion personal.</p>
            </div>
            <button class="profile-close-button" type="button" @click="profileModalOpen = false" aria-label="Cerrar">
              <X :size="22" />
            </button>
          </div>

          <div class="profile-modal-content">
            <form class="profile-section-card" @submit.prevent="saveProfile">
              <div class="profile-section-header personal">
                <UserRound :size="25" />
                <h3>Informacion personal</h3>
              </div>
              <div class="profile-form-grid profile-data-grid">
                <label class="profile-field">
                  <span><UserRound :size="24" /> Nombre</span>
                  <input v-model="profileForm.nombre" required />
                </label>
                <label class="profile-field">
                  <span><UserRound :size="24" /> Apellido</span>
                  <input v-model="profileForm.apellido" required />
                </label>
                <label class="profile-field">
                  <span><Mail :size="24" /> Correo</span>
                  <input v-model="profileForm.correo" disabled />
                </label>
                <label class="profile-field">
                  <span><ShieldCheck :size="24" /> Rol</span>
                  <input v-model="profileForm.rol" disabled />
                </label>
                <label class="profile-field">
                  <span><Phone :size="24" /> Telefono</span>
                  <input v-model="profileForm.telefono" />
                </label>
                <div class="profile-inline-actions">
                  <button class="profile-secondary-action" type="button" @click="profileModalOpen = false">Cerrar</button>
                  <button class="profile-primary-action" type="submit">
                    <Save :size="18" />
                    Guardar cambios
                  </button>
                </div>
              </div>
            </form>

            <form class="profile-section-card" @submit.prevent="savePassword">
              <div class="profile-section-header password">
                <Lock :size="25" />
                <h3>Cambiar contrasena</h3>
              </div>
              <div class="profile-form-grid password-change-grid">
                <label class="profile-field">
                  <span><Lock :size="24" /> Contrasena actual</span>
                  <div class="password-input-wrap">
                    <input v-model="passwordForm.password_actual" type="password" required placeholder="Ingresa tu contrasena actual" />
                    <EyeOff :size="24" />
                  </div>
                </label>
                <label class="profile-field">
                  <span><Lock :size="24" /> Nueva contrasena</span>
                  <div class="password-input-wrap">
                    <input v-model="passwordForm.password" type="password" minlength="8" required placeholder="Ingresa tu nueva contrasena" />
                    <EyeOff :size="24" />
                  </div>
                </label>
                <label class="profile-field">
                  <span><Lock :size="24" /> Confirmar nueva contrasena</span>
                  <div class="password-input-wrap">
                    <input v-model="passwordForm.password_confirmation" type="password" minlength="8" required placeholder="Confirma tu nueva contrasena" />
                    <EyeOff :size="24" />
                  </div>
                </label>
                <button class="profile-password-action" type="submit">
                  <KeyRound :size="23" />
                  Cambiar contrasena
                </button>
                <p class="profile-help"><Info :size="22" /> La nueva contrasena debe tener al menos 8 caracteres e incluir letras y numeros.</p>
              </div>
            </form>
            <p v-if="profileError" class="error-message">{{ profileError }}</p>
            <p v-if="profileMessage" class="success-message">{{ profileMessage }}</p>
            <p v-if="passwordError" class="error-message">{{ passwordError }}</p>
            <p v-if="passwordMessage" class="success-message">{{ passwordMessage }}</p>
          </div>
        </section>
      </div>

      <div v-if="logoutModalOpen" class="modal-backdrop" @click.self="logoutModalOpen = false">
        <section class="logout-card">
          <div class="logout-card-body">
            <div class="logout-icon-panel">
              <LogOut :size="38" />
            </div>
            <div class="logout-copy">
              <p class="eyebrow">Cerrar sesion</p>
              <h2>Confirmar salida</h2>
              <p>Se cerrara tu sesion actual y volveras a los anuncios publicos.</p>
              <p>Estas seguro de que deseas continuar?</p>
            </div>
            <button class="logout-close-button" type="button" @click="logoutModalOpen = false" aria-label="Cerrar">
              <X :size="22" />
            </button>
          </div>
          <div class="logout-actions">
            <button class="logout-cancel-action" type="button" @click="logoutModalOpen = false">Cancelar</button>
            <button class="logout-confirm-action" type="button" @click="closeSession">
              <LogOut :size="18" />
              Cerrar sesion
            </button>
          </div>
        </section>
      </div>
    </Teleport>
  </header>
</template>
