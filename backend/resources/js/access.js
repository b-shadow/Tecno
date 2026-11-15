import { authState, canManageCatalog, canManageUsers, isAuthenticated } from './services/auth'

// Reglas de acceso por pagina (antes en los meta de vue-router). La API valida cada rol en el servidor.
export const routeMeta = {
  '/dashboard': { private: true },
  '/inicio-vendedor': { private: true, sellerHome: true },
  '/usuarios': { private: true, admin: true },
  '/gestion-anuncios': { private: true },
  '/prospectos': { private: true },
  '/validacion-pagos': { private: true, catalog: true },
  '/alumnos': { private: true, catalog: true },
  '/seguimiento': { private: true },
  '/interesados': { private: true, catalog: true },
  '/agenda': { private: true },
  '/reportes': { private: true },
  '/reportes-comerciales': { private: true, catalog: true },
  '/notificaciones': { private: true },
}

/** Devuelve la ruta a la que hay que redirigir, o null si la pagina se puede mostrar. */
export function redirectFor({ path, fullPath }) {
  const meta = routeMeta[path] || {}
  const home = authState.usuario?.rol === 'vendedor' ? '/inicio-vendedor' : '/dashboard'

  if (meta.private && !isAuthenticated()) return `/login?redirect=${encodeURIComponent(fullPath)}`
  if (!meta.private && isAuthenticated()) return home
  if (path === '/dashboard' && authState.usuario?.rol === 'vendedor') return '/inicio-vendedor'
  if (meta.sellerHome && authState.usuario?.rol !== 'vendedor') return '/dashboard'
  if (meta.admin && !canManageUsers()) return home
  if (meta.catalog && !canManageCatalog()) return home

  return null
}
