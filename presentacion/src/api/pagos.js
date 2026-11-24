import { cliente } from './cliente'

// PagoController (CU6, enunciado 10): métodos de pago, órdenes con cuotas, comprobantes y validación.
const cuota = (orden, nro) => `/ordenes-pago/${orden}/cuotas/${nro}`
export const descuentos = () => cliente.get('/descuentos')
export const registrarMetodo = (documento, datos) => cliente.post(`/prospectos/${documento}/metodos-pago`, datos)
export const cambiarEstadoMetodo = (nro, estado) => cliente.patch(`/metodos-pago/${nro}/estado`, { estado })
export const crearOrden = (nroInteres, datos) => cliente.post(`/intereses/${nroInteres}/ordenes-pago`, datos)
export const registrarComprobante = (orden, nro, datos) => cliente.post(`${cuota(orden, nro)}/comprobante`, datos)
export const pagarConTarjeta = (orden, nro, nroMetodo) => cliente.post(`${cuota(orden, nro)}/pagar`, { nro_metodo: nroMetodo })
export const cuotas = (params) => cliente.get('/cuotas', { params })
export const aprobar = (orden, nro, observacion) => cliente.patch(`${cuota(orden, nro)}/aprobar`, { observacion })
export const rechazar = (orden, nro, observacion) => cliente.patch(`${cuota(orden, nro)}/rechazar`, { observacion })
export const comprobante = (nro) => cliente.get(`/comprobantes/${nro}`)
