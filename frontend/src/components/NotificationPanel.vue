<script setup>
import { Check } from '@lucide/vue'

defineProps({
  notificaciones: { type: Array, default: () => [] },
})

defineEmits(['mark-read'])
</script>

<template>
  <section class="table-surface">
    <div class="table-header">
      <div>
        <p class="eyebrow">Comunicacion</p>
        <h2>Notificaciones enviadas</h2>
      </div>
    </div>
    <div class="activity-list">
      <article v-for="notificacion in notificaciones" :key="notificacion.id" class="activity-item">
        <div class="notification-row">
          <strong>{{ notificacion.tipo }}</strong>
          <span class="badge" :class="notificacion.estado">{{ notificacion.estado }}</span>
        </div>
        <span>{{ notificacion.destinatario || notificacion.usuario?.correo }}</span>
        <p>{{ notificacion.mensaje }}</p>
        <small>{{ notificacion.fecha_envio }}</small>
        <button v-if="notificacion.estado !== 'leida'" class="icon-button" type="button" title="Marcar como leida" @click="$emit('mark-read', notificacion)">
          <Check :size="18" />
        </button>
      </article>
      <p v-if="notificaciones.length === 0" class="muted">Sin notificaciones registradas.</p>
    </div>
  </section>
</template>
