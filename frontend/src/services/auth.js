import { reactive } from 'vue'
import { getMe, login as loginRequest, logout as logoutRequest, updatePerfil, updatePerfilPassword } from './api'

const storageKey = 'crm_usuario'
const tokenKey = 'crm_token'

function readStoredUser() {
  try {
    return JSON.parse(localStorage.getItem(storageKey) || 'null')
  } catch {
    localStorage.removeItem(storageKey)
    localStorage.removeItem(tokenKey)
    return null
  }
}

export const authState = reactive({
  token: localStorage.getItem(tokenKey),
  usuario: readStoredUser(),
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

export async function login(credentials) {
  const data = await loginRequest(credentials)

  setSession(data)

  return data.usuario
}

export function setSession(data) {
  authState.token = data.token
  authState.usuario = data.usuario
  localStorage.setItem(tokenKey, data.token)
  localStorage.setItem(storageKey, JSON.stringify(data.usuario))
}

export async function refreshSession() {
  if (!authState.token) {
    return null
  }

  authState.usuario = await getMe()
  localStorage.setItem(storageKey, JSON.stringify(authState.usuario))

  return authState.usuario
}

export async function updateProfile(payload) {
  authState.usuario = await updatePerfil(payload)
  localStorage.setItem(storageKey, JSON.stringify(authState.usuario))

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
  localStorage.removeItem(tokenKey)
  localStorage.removeItem(storageKey)
}
