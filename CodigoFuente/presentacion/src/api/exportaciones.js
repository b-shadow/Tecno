import { cliente } from './cliente'

// ExportacionController (CU6): envío de matriculados al SIS.
export const pendientes = () => cliente.get('/exportaciones/pendientes')
export const exportar = () => cliente.post('/exportaciones')
export const registrarResultado = (nro, estado) => cliente.patch(`/exportaciones/${nro}`, { estado })
