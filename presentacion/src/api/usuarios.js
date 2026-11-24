import { cliente } from './cliente'

// UsuarioController (CU1).
const ruta = (correo) => `/usuarios/${encodeURIComponent(correo)}`
export const index = (params) => cliente.get('/usuarios', { params })
export const store = (datos) => cliente.post('/usuarios', datos)
export const update = (correo, datos) => cliente.put(ruta(correo), datos)
export const cambiarEstado = (correo, estado) => cliente.patch(`${ruta(correo)}/estado`, { estado })
export const vendedores = () => cliente.get('/vendedores')
