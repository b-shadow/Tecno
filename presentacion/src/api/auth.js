import { cliente } from './cliente'

// AuthController: sesión con token y perfil propio.
export const login = (credenciales) => cliente.post('/login', credenciales)
export const me = () => cliente.get('/me')
export const actualizarPerfil = (datos) => cliente.put('/perfil', datos)
export const cambiarPassword = (datos) => cliente.put('/perfil/password', datos)
export const logout = () => cliente.post('/logout')
