import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api',
  headers: {
    Accept: 'application/json',
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('crm_token')

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

export async function getSystemHealth() {
  const response = await api.get('/health')

  return response.data
}

export async function login(credentials) {
  const response = await api.post('/login', credentials)

  return response.data
}

export async function logout() {
  const response = await api.post('/logout')

  return response.data
}

export async function getMe() {
  const response = await api.get('/me')

  return response.data.usuario
}

export async function updatePerfil(payload) {
  const response = await api.put('/perfil', payload)

  return response.data.usuario
}

export async function updatePerfilPassword(payload) {
  const response = await api.put('/perfil/password', payload)

  return response.data
}

export async function listUsuarios(params = {}) {
  const response = await api.get('/usuarios', { params })

  return response.data.usuarios
}

export async function createUsuario(payload) {
  const response = await api.post('/usuarios', payload)

  return response.data.usuario
}

export async function updateUsuario(id, payload) {
  const response = await api.put(`/usuarios/${id}`, payload)

  return response.data.usuario
}

export async function changeUsuarioEstado(id, estado) {
  const response = await api.patch(`/usuarios/${id}/estado`, { estado })

  return response.data.usuario
}

export async function listAnuncios(params = {}) {
  const response = await api.get('/anuncios', { params })

  return response.data.anuncios
}

export async function listOfertas(params = {}) {
  const response = await api.get('/ofertas', { params })

  return response.data.ofertas
}

export async function registrarInteres(payload) {
  const response = await api.post('/registro-interes', payload)

  return response.data
}

export async function listDescuentos() {
  const response = await api.get('/descuentos')

  return response.data.descuentos
}

export async function listOrdenesPago() {
  const response = await api.get('/ordenes-pago')

  return response.data.ordenes
}

export async function listIntereses(params = {}) {
  const response = await api.get('/intereses', { params })

  return response.data.intereses
}

export async function tomarInteres(id) {
  const response = await api.patch(`/intereses/${id}/tomar`)

  return response.data.interes
}

export async function cambiarEstadoInteres(id, payload) {
  const response = await api.patch(`/intereses/${id}/estado`, payload)

  return response.data.interes
}

export async function crearOrdenPago(interesId, payload) {
  const response = await api.post(`/intereses/${interesId}/ordenes-pago`, payload)

  return response.data.orden
}

export async function listProspectos(params = {}) {
  const response = await api.get('/prospectos', { params })

  return response.data.prospectos
}

export async function saveProspecto(payload, id = null) {
  const response = id ? await api.put(`/prospectos/${id}`, payload) : await api.post('/prospectos', payload)

  return response.data.prospecto
}

export async function asignarProspecto(id, vendedor_id) {
  const response = await api.patch(`/prospectos/${id}/asignar`, { vendedor_id })

  return response.data.prospecto
}

export async function cambiarEstadoProspecto(id, estado) {
  const response = await api.patch(`/prospectos/${id}/estado`, { estado })

  return response.data.prospecto
}

export async function importarProspectos(payload) {
  const response = await api.post('/prospectos/importar', payload)

  return response.data
}

export async function listSolicitudesCompra() {
  const response = await api.get('/solicitudes-compra')

  return response.data.solicitudes
}

export async function generarPago(solicitud_compra_id) {
  const response = await api.post('/pagos/generar', { solicitud_compra_id })

  return response.data.pago
}

export async function generarPagoOrden(orden_pago_id) {
  const response = await api.post('/pagos/generar', { orden_pago_id })

  return response.data.pago
}

export async function getPago(id) {
  const response = await api.get(`/pagos/${id}`)

  return response.data.pago
}

export async function listPagos(params = {}) {
  const response = await api.get('/pagos', { params })

  return response.data.pagos
}

export async function subirComprobante(payload) {
  const response = await api.post('/comprobantes', payload)

  return response.data
}

export async function aprobarPago(id, observacion = '') {
  const response = await api.patch(`/pagos/${id}/aprobar`, { observacion })

  return response.data
}

export async function rechazarPago(id, observacion) {
  const response = await api.patch(`/pagos/${id}/rechazar`, { observacion })

  return response.data.pago
}

export async function listInteracciones(prospectoId) {
  const response = await api.get(`/prospectos/${prospectoId}/interacciones`)

  return response.data.interacciones
}

export async function registrarInteraccion(payload) {
  const response = await api.post('/interacciones', payload)

  return response.data.interaccion
}

export async function listRecordatorios(params = {}) {
  const response = await api.get('/recordatorios', { params })

  return response.data.recordatorios
}

export async function crearRecordatorio(payload) {
  const response = await api.post('/recordatorios', payload)

  return response.data.recordatorio
}

export async function completarRecordatorio(id) {
  const response = await api.patch(`/recordatorios/${id}/completar`)

  return response.data.recordatorio
}

export async function cancelarRecordatorio(id) {
  const response = await api.patch(`/recordatorios/${id}/cancelar`)

  return response.data.recordatorio
}

export async function confirmarInscripcion(solicitud_compra_id) {
  const response = await api.post('/inscripciones/confirmar', { solicitud_compra_id })

  return response.data
}

export async function listInscripciones() {
  const response = await api.get('/inscripciones')

  return response.data.inscripciones
}

export async function listComisiones() {
  const response = await api.get('/comisiones')

  return response.data.comisiones
}

export async function getResumenComisiones() {
  const response = await api.get('/comisiones/resumen')

  return response.data
}

export async function pagarComisionesVendedor(vendedorId) {
  const response = await api.patch(`/comisiones/vendedores/${vendedorId}/pagar`)

  return response.data
}

export async function getReporteAdministrativo(params = {}) {
  const response = await api.get('/reportes/administrativos', { params })

  return response.data
}

export async function getDashboardMetricas() {
  const response = await api.get('/dashboard/metricas')

  return response.data
}

export async function getReporteComercial(params = {}) {
  const response = await api.get('/reportes/comerciales', { params })

  return response.data
}

export async function getReporteListado(params = {}) {
  const response = await api.get('/reportes/listado', { params })

  return response.data
}

export async function getEstadisticasVendedor(params = {}) {
  const response = await api.get('/estadisticas/vendedor', { params })

  return response.data.estadisticas
}

export async function enviarNotificacion(payload) {
  const response = await api.post('/notificaciones/enviar', payload)

  return response.data.notificacion
}

export async function listNotificaciones() {
  const response = await api.get('/notificaciones')

  return response.data.notificaciones
}

export async function marcarNotificacionLeida(id) {
  const response = await api.patch(`/notificaciones/${id}/leida`)

  return response.data.notificacion
}

export async function prepararExportacionAcademica() {
  const response = await api.get('/exportaciones/preparar')

  return response.data
}

export async function exportarAcademico() {
  const response = await api.post('/exportaciones/academico')

  return response.data
}

export async function actualizarExportacion(id, payload) {
  const response = await api.patch(`/exportaciones/${id}`, payload)

  return response.data.exportacion
}

export async function listExportaciones() {
  const response = await api.get('/exportaciones')

  return response.data.exportaciones
}
