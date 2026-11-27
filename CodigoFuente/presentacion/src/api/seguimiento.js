import { cliente } from './cliente'

// SeguimientoController (CU7 interacciones y recordatorios; CU6 inscripciones y comisiones).
export const registrarInteraccion = (nro, datos) => cliente.post(`/intereses/${nro}/interacciones`, datos)
export const crearRecordatorio = (nro, datos) => cliente.post(`/intereses/${nro}/recordatorios`, datos)
export const recordatorios = (params) => cliente.get('/recordatorios', { params })
export const completarRecordatorio = (nro, resultado) => cliente.patch(`/recordatorios/${nro}/completar`, { resultado })
export const cancelarRecordatorio = (nro) => cliente.patch(`/recordatorios/${nro}/cancelar`)
export const inscripciones = () => cliente.get('/inscripciones')
export const comisiones = () => cliente.get('/comisiones')
export const resumenComisiones = () => cliente.get('/comisiones/resumen')
export const pagarComisiones = (correo) => cliente.patch(`/comisiones/vendedores/${encodeURIComponent(correo)}/pagar`)
export const actualizarConfiguracionComision = (porcentaje) => cliente.put('/configuracion/comision', { porcentaje })
