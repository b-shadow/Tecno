import axios from 'axios'
import { clearStoredSession, getStoredToken } from '../servicios/session'

// Único cliente HTTP de la capa de presentación hacia la API REST de Laravel (capa 2).
// Las páginas no lo usan directo: llaman a las funciones de api/<area>.js.
export const cliente = axios.create({
  baseURL: `${import.meta.env.BASE_URL}api`,
  headers: { Accept: 'application/json' },
})

cliente.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

cliente.interceptors.response.use((response) => response, (error) => {
  const estado = error.response?.status
  if (estado === 401 && !error.config?.url?.endsWith('/login')) {
    clearStoredSession()
    window.dispatchEvent(new Event('crm:session-expired'))
  }
  // Permiso retirado en la matriz: se relee el menú del rol para que la UI deje de ofrecer la página.
  if (estado === 403) window.dispatchEvent(new Event('crm:forbidden'))
  return Promise.reject(error)
})
