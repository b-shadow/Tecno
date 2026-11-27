import { cliente } from './cliente'

// NotificacionController (CU7).
export const index = () => cliente.get('/notificaciones')
export const enviar = (datos) => cliente.post('/notificaciones', datos)
export const marcarLeida = (nro) => cliente.patch(`/notificaciones/${nro}/leida`)
