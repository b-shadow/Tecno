import { cliente } from './cliente'

// ReporteController (CU8): dashboard, estadísticas porcentuales y listados.
export const dashboard = () => cliente.get('/dashboard')
export const estadisticasVendedor = () => cliente.get('/estadisticas/vendedor')
export const estadisticas = (params) => cliente.get('/reportes/estadisticas', { params })
export const listado = (params) => cliente.get('/reportes/listado', { params })
