<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRight, BarChart3, BookOpen, CreditCard, Eye, EyeOff, Lock, Mail, MessageCircle, ShieldCheck } from '@lucide/vue'
import { authState, isAuthenticated, login } from '../services/auth'

const router = useRouter()
const route = useRoute()
const loading = ref(false)
const error = ref('')
const remember = ref(true)
const showPassword = ref(false)
const alreadyAuthenticated = computed(() => isAuthenticated())
const form = ref({
  correo: '',
  password: '',
})

const benefits = [
  {
    icon: BookOpen,
    title: 'Gestion comercial',
    text: 'Consulta interesados, agenda seguimientos y registra avances comerciales.',
    tone: 'green',
  },
  {
    icon: MessageCircle,
    title: 'Seguimiento por WhatsApp',
    text: 'Documenta llamadas, mensajes y acuerdos realizados fuera de la plataforma.',
    tone: 'blue',
  },
  {
    icon: CreditCard,
    title: 'Ordenes y pagos',
    text: 'Genera ordenes, registra comprobantes y coordina la validacion de pagos.',
    tone: 'purple',
  },
  {
    icon: BarChart3,
    title: 'Control academico',
    text: 'Coordina alumnos inscritos, reportes y estados de integracion academica.',
    tone: 'orange',
  },
]

async function submit() {
  loading.value = true
  error.value = ''

  try {
    const usuario = await login(form.value)
    const defaultRedirect = '/dashboard'
    const redirect = typeof route.query.redirect === 'string' && route.query.redirect !== '/login' ? route.query.redirect : defaultRedirect
    await router.replace(redirect)
  } catch (exception) {
    error.value = exception.response?.data?.mensaje || 'No se pudo iniciar sesion.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (isAuthenticated()) {
    router.replace('/dashboard')
  }
})
</script>

<template>
  <section v-if="!alreadyAuthenticated" class="login-hero-page">
    <form class="login-card" @submit.prevent="submit">
      <div>
        <p class="eyebrow">Acceso interno</p>
        <h2>Iniciar sesion</h2>
        <p>Ingresa para gestionar interesados, agenda comercial, pagos y reportes del equipo.</p>
      </div>

      <label class="login-field">
        <span>Correo</span>
        <div class="login-input-wrap">
          <Mail :size="23" />
          <input v-model="form.correo" type="email" autocomplete="email" placeholder="tu.correo@ejemplo.com" required />
        </div>
      </label>

      <label class="login-field">
        <span>Contrasena</span>
        <div class="login-input-wrap">
          <Lock :size="23" />
          <input v-model="form.password" :type="showPassword ? 'text' : 'password'" autocomplete="current-password" placeholder="********" required />
          <button type="button" :title="showPassword ? 'Ocultar contrasena' : 'Mostrar contrasena'" @click="showPassword = !showPassword">
            <EyeOff v-if="showPassword" :size="23" />
            <Eye v-else :size="23" />
          </button>
        </div>
      </label>

      <div class="login-options-row">
        <label class="remember-check">
          <input v-model="remember" type="checkbox" />
          <span>Recordarme</span>
        </label>
        <button type="button">Olvidaste tu contrasena?</button>
      </div>

      <p v-if="error" class="error-message">{{ error }}</p>

      <button class="login-submit" type="submit" :disabled="loading">
        {{ loading ? 'Ingresando...' : 'Ingresar' }}
        <ArrowRight :size="24" />
      </button>

      <div class="login-register-link">
        <span></span>
        <p>Acceso exclusivo para vendedores y coordinadores.</p>
        <span></span>
      </div>

      <p class="login-security-note">
        <ShieldCheck :size="22" />
        Tus datos estan protegidos y encriptados.
      </p>
    </form>

    <section class="login-info-panel">
      <div class="login-bg-orb one"></div>
      <div class="login-bg-orb two"></div>
      <div class="login-bg-orb three"></div>

      <div class="login-info-heading">
        <p class="eyebrow">Panel comercial NEXO</p>
        <h2>Gestiona interesados, pagos y seguimiento academico</h2>
        <p>Espacio de trabajo para vendedores y coordinadores: organiza contactos, registra actividades, valida pagos y prepara la integracion de alumnos.</p>
      </div>

      <div class="login-benefit-grid">
        <article v-for="benefit in benefits" :key="benefit.title" class="login-benefit-card">
          <span :class="benefit.tone">
            <component :is="benefit.icon" :size="36" />
          </span>
          <div>
            <h3>{{ benefit.title }}</h3>
            <p>{{ benefit.text }}</p>
          </div>
        </article>
      </div>

      <div class="login-bottom-banner">
        <div>
          <h3>Operacion comercial centralizada</h3>
          <p>Unifica seguimiento, ordenes de pago y reportes para mantener el proceso claro entre ventas y coordinacion.</p>
        </div>
        <div>
          <span>Agenda comercial</span>
          <span>Validacion de pagos</span>
          <span>Reportes internos</span>
        </div>
      </div>
    </section>
  </section>
</template>
