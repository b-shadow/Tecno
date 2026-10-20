import { reactive } from 'vue'
import { getMe, login as loginRequest, logout as logoutRequest, updatePerfil, updatePerfilPassword } from './api'
import { clearStoredSession, persistSession, readSession } from './session'

export const authState = reactive(readSession())

window.addEventListener('crm:session-expired', () => {
  authState.token = null
  authState.usuario = null
})

export function isAuthenticated() {
  return Boolean(authState.token && authState.usuario)
}

export function canManageUsers() {
  return authState.usuario?.rol === 'administrador'
}

export function canManageCatalog() {
  return ['administrador', 'coordinador'].includes(authState.usuario?.rol)
}

export async function login(credentials, remember = true) {
  const data = await loginRequest(credentials)

  setSession(data, remember)

  return data.usuario
}

export function setSession(data, remember = true) {
  authState.token = data.token
  authState.usuario = data.usuario
  authState.remember = remember
  persistSession(data, remember)
}

export async function refreshSession() {
  if (!authState.token) {
    return null
  }

  authState.usuario = await getMe()
  persistSession(authState, authState.remember)

  return authState.usuario
}

export async function updateProfile(payload) {
  authState.usuario = await updatePerfil(payload)
  persistSession(authState, authState.remember)

  return authState.usuario
}

export async function changePassword(payload) {
  return updatePerfilPassword(payload)
}

export async function logout() {
  if (authState.token) {
    try {
      await logoutRequest()
    } catch {
      // Local cleanup is still required when the server session is already gone.
    }
  }

  authState.token = null
  authState.usuario = null
  clearStoredSession()
}
