import { cliente } from './cliente'

// SeguridadController (CU1): matriz de acceso y bitácora.
export const matriz = () => cliente.get('/matriz')
export const asignar = (datos) => cliente.put('/matriz', datos)
export const bitacora = (params) => cliente.get('/bitacora', { params })
export const resumen = () => cliente.get('/bitacora/resumen')
