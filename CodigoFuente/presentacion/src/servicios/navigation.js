import { useLocation, useMatches } from 'react-router-dom'

// Navegación de la SPA (react-router). Las rutas internas ('/agenda') no llevan la base del despliegue:
// el router la agrega (basename = /inf513/grupo05sa/proyecto2 en la facultad).
let router = null
export const fijarRouter = (r) => { router = r }

/** Ruta interna actual: path, query y fullPath. */
export function useAppRoute() {
  const { pathname, search } = useLocation()
  return { path: pathname, query: Object.fromEntries(new URLSearchParams(search)), fullPath: pathname + search }
}

/** Ruta con la que la página cuenta visitas: la propia, o /error si no existe. */
export function useRecursoActual() {
  const { path } = useAppRoute()
  const matches = useMatches()
  return matches.at(-1)?.handle?.recurso || path
}

export function go(path, { replace = false } = {}) {
  router?.navigate(path, { replace })
}
