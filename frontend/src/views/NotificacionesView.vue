<script setup>
import { onMounted, ref } from 'vue'
import NotificationPanel from '../components/NotificationPanel.vue'
import { enviarNotificacion, listNotificaciones, listUsuarios, marcarNotificacionLeida } from '../services/api'

const usuarios = ref([])
const notificaciones = ref([])
const form = ref({ usuario_id: '', destinatario: '', tipo: 'Cambio importante', mensaje: '' })
const message = ref('')
const error = ref('')

async function loadData() {
  notificaciones.value = await listNotificaciones()
  try {
    usuarios.value = await listUsuarios()
  } catch {
    usuarios.value = []
  }
}

async function send() {
  message.value = ''
  error.value = ''
  try {
    await enviarNotificacion({
      ...form.value,
      usuario_id: form.value.usuario_id || null,
      destinatario: form.value.destinatario || null,
    })
    form.value = { usuario_id: '', destinatario: '', tipo: 'Cambio importante', mensaje: '' }
    message.value = 'Notificacion enviada y registrada.'
    await loadData()
  } catch (exception) {
    error.value = exception.response?.data?.message || 'No se pudo enviar la notificacion.'
  }
}

async function markRead(notificacion) {
  await marcarNotificacionLeida(notificacion.id)
  await loadData()
}

onMounted(loadData)
</script>

<template>
  <section class="users-layout">
    <form class="form-surface user-form" @submit.prevent="send">
      <p class="eyebrow">Correo</p>
      <h2>Enviar notificacion</h2>
      <div class="form-grid">
        <label class="full-field">Usuario interno
          <select v-model="form.usuario_id">
            <option value="">Sin usuario interno</option>
            <option v-for="usuario in usuarios" :key="usuario.id" :value="usuario.id">{{ usuario.nombre }} {{ usuario.apellido }} - {{ usuario.rol }}</option>
          </select>
        </label>
        <label class="full-field">Correo externo<input v-model="form.destinatario" type="email" placeholder="correo@dominio.com" /></label>
        <label class="full-field">Tipo
          <select v-model="form.tipo">
            <option>Confirmacion de registro</option>
            <option>Comprobante recibido</option>
            <option>Resultado de validacion de pago</option>
            <option>Nuevo prospecto asignado</option>
            <option>Recordatorio pendiente</option>
            <option>Cambio importante</option>
          </select>
        </label>
        <label class="full-field">Mensaje<textarea v-model="form.mensaje" required></textarea></label>
      </div>
      <p v-if="message" class="success-message">{{ message }}</p>
      <p v-if="error" class="error-message">{{ error }}</p>
      <div class="form-actions"><button type="submit">Enviar</button></div>
    </form>

    <NotificationPanel :notificaciones="notificaciones" @mark-read="markRead" />
  </section>
</template>
