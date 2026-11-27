import { cliente } from './cliente'

// MotivoController (CU5).
const ruta = (nombre) => `/motivos/${encodeURIComponent(nombre)}`
export const index = () => cliente.get('/motivos')
export const store = (datos) => cliente.post('/motivos', datos)
export const update = (nombre, datos) => cliente.put(ruta(nombre), datos)
export const destroy = (nombre) => cliente.delete(ruta(nombre))
