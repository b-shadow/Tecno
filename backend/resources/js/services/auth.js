import { useSyncExternalStore } from 'react'
import { api } from './api'
import { clearStoredSession, persistSession, readSession } from './session'

// Estado de sesión compartido (usuario, menú dinámico y permisos de su rol). Cada cambio reemplaza el objeto.
let estado = readSession()
const oyentes = new Set()

function fijar(nuevo) {
  estado = { ...estado, ...nuevo }
  oyentes.forEach((oyente) => oyente())
}

window.addEventListener('crm:session-expired', () => fijar({ token: null, usuario: null, menu: [], permisos: {} }))

export function useAuth() {
  return useSyncExternalStore((oyente) => {
    oyentes.add(oyente)
    return () => oyentes.delete(oyente)
  }, () => estado)
}

export const authState = () => estado
export const isAuthenticated = () => Boolean(estado.token && estado.usuario)

/** Nivel de acceso del rol sobre un recurso: 0 nada, 1 lectura, 2 modificación, 3 eliminación. */
export function nivel(recurso, s = estado) {
  return { lectura: 1, modificacion: 2, eliminacion: 3 }[s.permisos?.[recurso]] || 0
}
export const puede = (recurso, minimo = 'lectura', s = estado) => nivel(recurso, s) >= { lectura: 1, modificacion: 2, eliminacion: 3 }[minimo]

export async function login(credenciales, remember = true) {
  const { data } = await api.post('/login', credenciales)
  persistSession(data, remember)
  fijar({ token: data.token, usuario: data.usuario, menu: data.menu, permisos: data.permisos, remember })
  return data
}

export async function refreshSession() {
  if (!estado.token) return null
  const { data } = await api.get('/me')
  const nuevo = { ...estado, ...data }
  persistSession(nuevo, estado.remember)
  fijar(data)
  return data.usuario
}

export async function updateProfile(payload) {
  const { data } = await api.put('/perfil', payload)
  const nuevo = { ...estado, usuario: data.usuario }
  persistSession(nuevo, estado.remember)
  fijar({ usuario: data.usuario })
  return data
}

export async function logout() {
  if (estado.token) {
    try {
      await api.post('/logout')
    } catch {
      // Si la sesión ya no existe en el servidor igual hay que limpiar la local.
    }
  }
  clearStoredSession()
  fijar({ token: null, usuario: null, menu: [], permisos: {} })
}
