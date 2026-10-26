import { cliente } from './cliente'

// InteresController (CU3 asignación, CU4 embudo Kanban, CU5 pérdida con motivo).
export const index = (params) => cliente.get('/intereses', { params })
export const show = (nro) => cliente.get(`/intereses/${nro}`)
export const mover = (nro, datos) => cliente.patch(`/intereses/${nro}/estado`, datos)
export const asignar = (nro, vendedorCorreo) => cliente.patch(`/intereses/${nro}/asignar`, { vendedor_correo: vendedorCorreo })
export const distribuir = () => cliente.post('/intereses/distribuir')
