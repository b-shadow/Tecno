<script setup>
import {
  BarChart3,
  BadgeDollarSign,
  CalendarDays,
  CreditCard,
  GraduationCap,
  Mail,
  Megaphone,
  Menu,
  NotebookTabs,
  UserRound,
  Users,
} from '@lucide/vue'
import unexoLogo from '../../assets/UNEXO.png'
import { authState } from '../services/auth'

const props = defineProps({
  collapsed: { type: Boolean, default: false },
})

const emit = defineEmits(['toggle-sidebar'])

const items = [
  { label: 'Dashboard', path: '/dashboard', icon: BarChart3, enabled: true },
  { label: 'Usuarios', path: '/usuarios', icon: Users, enabled: true, admin: true },
  { label: 'Anuncios', path: '/gestion-anuncios', icon: Megaphone, enabled: true, catalog: true },
  { label: 'Prospectos', path: '/prospectos', icon: UserRound, enabled: true },
  { label: 'Interesados', path: '/interesados', icon: UserRound, enabled: true },
  { label: 'Agenda', path: '/agenda', icon: NotebookTabs, enabled: true },
  { label: 'Validacion pagos', path: '/validacion-pagos', icon: CreditCard, enabled: true, catalog: true },
  { label: 'Alumnos e integracion', path: '/alumnos', icon: GraduationCap, enabled: true, catalog: true },
  { label: 'Ventas y comisiones', path: '/seguimiento', icon: BadgeDollarSign, enabled: true },
  { label: 'Reportes', path: '/reportes', icon: BarChart3, enabled: true },
  { label: 'Notificaciones', path: '/notificaciones', icon: Mail, enabled: true },
]

const visibleItems = () => {
  const role = authState.usuario?.rol
  const roleItems = role === 'vendedor'
    ? [
        { label: 'Inicio', path: '/inicio-vendedor', icon: CalendarDays, enabled: true },
        ...items.filter((entry) => entry.path !== '/dashboard'),
      ]
    : items

  return roleItems.filter((entry) => (!entry.admin || role === 'administrador') && (!entry.catalog || ['administrador', 'coordinador'].includes(role)))
}

function closeMobileMenu() {
  if (window.matchMedia('(max-width: 960px)').matches && !props.collapsed) {
    emit('toggle-sidebar')
  }
}
</script>

<template>
  <aside class="sidebar" :class="{ collapsed }">
    <button class="brand" type="button" title="Ocultar o mostrar menu" @click="$emit('toggle-sidebar')">
      <div class="brand-mark">
        <img :src="unexoLogo" alt="UNEXO" />
      </div>
      <div class="brand-text">
        <strong>Educativo</strong>
        <span>Comercial</span>
      </div>
      <Menu class="brand-menu-icon" :size="23" />
    </button>

    <nav class="nav-list" aria-label="Modulos principales">
      <RouterLink
        v-for="item in visibleItems()"
        :key="item.label"
        :to="item.path"
        class="nav-item"
        :class="{ disabled: !item.enabled }"
        :title="collapsed ? item.label : ''"
        @click="closeMobileMenu"
      >
        <component :is="item.icon" :size="19" aria-hidden="true" />
        <span v-if="!collapsed">{{ item.label }}</span>
      </RouterLink>
    </nav>

    <div v-if="!collapsed" class="sidebar-footer">
      <span>CRM Educativo</span>
      <small>UAGRM</small>
    </div>
  </aside>
</template>
