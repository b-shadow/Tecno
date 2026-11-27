import { cliente } from './cliente'

// NPago (CU6): órdenes con cuotas, envío automático, Stripe Checkout Sandbox, enlaces públicos y validación histórica.
const cuota = (orden, nro) => `/ordenes-pago/${orden}/cuotas/${nro}`
export const descuentos = () => cliente.get('/descuentos')
export const crearSetupTarjeta = (documento, nroTarjeta) => cliente.post(`/prospectos/${encodeURIComponent(documento)}/metodos-pago/stripe-setup`, { nro_tarjeta: nroTarjeta || undefined })
export const cambiarEstadoMetodo = (nro, estado) => cliente.patch(`/metodos-pago/${nro}/estado`, { estado })
export const crearOrden = (nroInteres, datos) => cliente.post(`/intereses/${nroInteres}/ordenes-pago`, datos)
export const anularOrden = (orden, motivo) => cliente.patch(`/ordenes-pago/${orden}/anular`, { motivo })
export const crearCheckout = (orden, nro) => cliente.post(`${cuota(orden, nro)}/checkout`)
export const confirmarCheckout = (sessionId) => cliente.get(`/pagos/stripe/sesiones/${encodeURIComponent(sessionId)}`)
export const cancelarCheckout = (sessionId) => cliente.post(`/pagos/stripe/sesiones/${encodeURIComponent(sessionId)}/cancelar`)
export const consultarRetornoPublico = (sessionId, token) => cliente.get(`/pagos/publico/sesiones/${encodeURIComponent(sessionId)}`, { params: { token } })
export const cancelarRetornoPublico = (sessionId, token) => cliente.post(`/pagos/publico/sesiones/${encodeURIComponent(sessionId)}/cancelar`, { token })
export const abrirEnlaceCuotaPublico = (token) => cliente.get(`/pagos/publico/cuotas/${encodeURIComponent(token)}`)
export const cuotas = (params) => cliente.get('/cuotas', { params })
export const aprobar = (orden, nro, observacion) => cliente.patch(`${cuota(orden, nro)}/aprobar`, { observacion })
export const rechazar = (orden, nro, observacion) => cliente.patch(`${cuota(orden, nro)}/rechazar`, { observacion })
export const comprobante = (nro) => cliente.get(`/comprobantes/${nro}`)
