// Acceso a páginas desde el cliente, con el mismo menú que viene de la BD (la API vuelve a validar cada llamada).
export const PUBLICAS = ['/anuncios', '/login']

export const PRIVADAS = [
  '/dashboard', '/inicio-vendedor', '/embudo', '/prospectos', '/interesados', '/agenda', '/motivos-perdida',
  '/validacion-pagos', '/alumnos', '/gestion-anuncios', '/seguimiento', '/reportes', '/notificaciones',
  '/usuarios', '/matriz-acceso', '/bitacora',
  '/pagos/confirmacion', '/pagos/cancelado',
]

const RECURSO_POR_RUTA = {
  '/pagos/confirmacion': '/agenda',
  '/pagos/cancelado': '/agenda',
}

/** Primera página del menú del rol (administrador y coordinador: Dashboard; vendedor: Mi día). */
export function inicio(sesion) {
  return sesion.menu?.[0]?.ruta || '/anuncios'
}

/** Ruta a la que hay que redirigir, o null si la página se puede mostrar. */
export function redirectFor({ path, fullPath }, sesion) {
  const dentro = Boolean(sesion.token && sesion.usuario)
  if (PRIVADAS.includes(path)) {
    if (!dentro) return `/login?redirect=${encodeURIComponent(fullPath)}`
    const recurso = RECURSO_POR_RUTA[path] || path
    if (!sesion.menu?.some((m) => m.ruta === recurso)) return inicio(sesion)
    return null
  }
  if (path === '/login' && dentro) return inicio(sesion)
  return null
}
