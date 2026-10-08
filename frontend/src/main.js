import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import HomeView from './views/HomeView.vue'
import LoginView from './views/LoginView.vue'
import DashboardView from './views/DashboardView.vue'
import UsuariosView from './views/UsuariosView.vue'
import OfertasView from './views/OfertasView.vue'
import ProspectosView from './views/ProspectosView.vue'
import ValidacionPagosView from './views/ValidacionPagosView.vue'
import SeguimientoView from './views/SeguimientoView.vue'
import DashboardReportesView from './views/DashboardReportesView.vue'
import ReportesComercialesView from './views/ReportesComercialesView.vue'
import NotificacionesView from './views/NotificacionesView.vue'
import AgendaView from './views/AgendaView.vue'
import AlumnosView from './views/AlumnosView.vue'
import VendedorInicioView from './views/VendedorInicioView.vue'
import InteresadosView from './views/InteresadosView.vue'
import { authState, canManageCatalog, canManageUsers, isAuthenticated } from './services/auth'
import './style.css'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/anuncios' },
    { path: '/inicio', name: 'inicio', component: HomeView },
    { path: '/anuncios', name: 'anuncios-publicos', component: OfertasView },
    { path: '/ofertas', redirect: '/anuncios' },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/dashboard', name: 'dashboard', component: DashboardView, meta: { private: true } },
    { path: '/inicio-vendedor', name: 'inicio-vendedor', component: VendedorInicioView, meta: { private: true, sellerHome: true } },
    { path: '/usuarios', name: 'usuarios', component: UsuariosView, meta: { private: true, admin: true } },
    { path: '/gestion-anuncios', name: 'anuncios', component: OfertasView, meta: { private: true } },
    { path: '/prospectos', name: 'prospectos', component: ProspectosView, meta: { private: true } },
    { path: '/validacion-pagos', name: 'validacion-pagos', component: ValidacionPagosView, meta: { private: true, catalog: true } },
    { path: '/alumnos', name: 'alumnos', component: AlumnosView, meta: { private: true, catalog: true } },
    { path: '/seguimiento', name: 'seguimiento', component: SeguimientoView, meta: { private: true } },
    { path: '/interesados', name: 'interesados', component: InteresadosView, meta: { private: true } },
    { path: '/agenda', name: 'agenda', component: AgendaView, meta: { private: true } },
    { path: '/chats', redirect: '/agenda' },
    { path: '/pagos', redirect: '/agenda' },
    { path: '/reportes', name: 'reportes', component: DashboardReportesView, meta: { private: true } },
    { path: '/reportes-comerciales', name: 'reportes-comerciales', component: ReportesComercialesView, meta: { private: true, catalog: true } },
    { path: '/estadisticas-vendedor', redirect: '/inicio-vendedor' },
    { path: '/notificaciones', name: 'notificaciones', component: NotificacionesView, meta: { private: true } },
    { path: '/comisiones', redirect: '/seguimiento' },
    { path: '/exportaciones', redirect: '/alumnos' },
  ],
})

router.beforeEach((to) => {
  const sellerHome = authState.usuario?.rol === 'vendedor' ? { name: 'inicio-vendedor' } : { name: 'dashboard' }

  if (to.meta.private && !isAuthenticated()) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (!to.meta.private && isAuthenticated()) {
    return sellerHome
  }

  if (to.name === 'dashboard' && authState.usuario?.rol === 'vendedor') {
    return { name: 'inicio-vendedor' }
  }

  if (to.meta.sellerHome && authState.usuario?.rol !== 'vendedor') {
    return { name: 'dashboard' }
  }

  if (to.meta.admin && !canManageUsers()) {
    return sellerHome
  }

  if (to.meta.catalog && !canManageCatalog()) {
    return sellerHome
  }

  if (to.name === 'login' && isAuthenticated()) return sellerHome
})

createApp(App).use(router).mount('#app')
