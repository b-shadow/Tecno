import { router, usePage } from '@inertiajs/react'

// Base de la app tal como la publica Laravel (url('/')): '' en local, '/inf513/grupo05sa/proyecto2' en la facultad.
const base = new URL(document.querySelector('meta[name="app-base"]')?.content || window.location.origin)
  .pathname.replace(/\/$/, '')

/** Ruta interna ('/agenda') -> URL real de la app. */
export function appUrl(path) {
  return `${base}${path}`
}

/** URL real -> ruta interna sin la base. */
export function appPath(pathname) {
  const path = pathname.startsWith(base) ? pathname.slice(base.length) : pathname
  return path || '/'
}

/** Ruta interna actual: path, query y fullPath de la página Inertia. */
export function useAppRoute() {
  const { url } = usePage()
  const [pathname, search = ''] = url.split('?')
  const path = appPath(pathname)
  return { path, query: Object.fromEntries(new URLSearchParams(search)), fullPath: search ? `${path}?${search}` : path }
}

export function go(path, options = {}) {
  router.visit(appUrl(path), options)
}
