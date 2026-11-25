import { cliente } from './cliente'

// NPago (CU6, enunciado 10): métodos de pago, órdenes con cuotas, comprobantes, anulación y Stripe Checkout Sandbox.
const cuota = (orden, nro) => `/ordenes-pago/${orden}/cuotas/${nro}`
export const descuentos = () => cliente.get('/descuentos')
export const registrarMetodo = (documento, datos) => cliente.post(`/prospectos/${encodeURIComponent(documento)}/metodos-pago`, datos)
export const crearSetupTarjeta = (documento, nroTarjeta) => cliente.post(`/prospectos/${encodeURIComponent(documento)}/metodos-pago/stripe-setup`, { nro_tarjeta: nroTarjeta || undefined })
export const cambiarEstadoMetodo = (nro, estado) => cliente.patch(`/metodos-pago/${nro}/estado`, { estado })
export const crearOrden = (nroInteres, datos) => cliente.post(`/intereses/${nroInteres}/ordenes-pago`, datos)
export const anularOrden = (orden, motivo) => cliente.patch(`/ordenes-pago/${orden}/anular`, { motivo })
export const registrarComprobante = (orden, nro, datos) => cliente.post(`${cuota(orden, nro)}/comprobante`, datos)
export const crearCheckout = (orden, nro) => cliente.post(`${cuota(orden, nro)}/checkout`)
export const confirmarCheckout = (sessionId) => cliente.get(`/pagos/stripe/sesiones/${encodeURIComponent(sessionId)}`)
export const cancelarCheckout = (sessionId) => cliente.post(`/pagos/stripe/sesiones/${encodeURIComponent(sessionId)}/cancelar`)
export const cuotas = (params) => cliente.get('/cuotas', { params })
export const aprobar = (orden, nro, observacion) => cliente.patch(`${cuota(orden, nro)}/aprobar`, { observacion })
export const rechazar = (orden, nro, observacion) => cliente.patch(`${cuota(orden, nro)}/rechazar`, { observacion })
export const comprobante = (nro) => cliente.get(`/comprobantes/${nro}`)
