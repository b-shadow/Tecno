import axios from 'axios'
import { appUrl } from './navigation'
import { clearStoredSession, getStoredToken } from './session'

// Cliente HTTP de la capa de presentación hacia la API REST de Laravel (capa 2).
export const api = axios.create({
  baseURL: appUrl('/api'),
  headers: { Accept: 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = getStoredToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use((response) => response, (error) => {
  if (error.response?.status === 401 && !error.config?.url?.endsWith('/login')) {
    clearStoredSession()
    window.dispatchEvent(new Event('crm:session-expired'))
  }
  return Promise.reject(error)
})

/** Descarga un CSV con BOM (Excel) escapando celdas que empiezan como fórmula. */
export function descargarCsv(nombre, filas) {
  if (!filas.length) return
  const columnas = Object.keys(filas[0])
  const celda = (valor) => {
    let texto = valor == null ? '' : String(valor)
    if (/^[=+\-@\t\r]/.test(texto)) texto = `'${texto}`
    return `"${texto.replaceAll('"', '""')}"`
  }
  const contenido = [columnas.map(celda).join(','), ...filas.map((f) => columnas.map((c) => celda(f[c])).join(','))].join('\r\n')
  const enlace = document.createElement('a')
  enlace.href = URL.createObjectURL(new Blob(['﻿' + contenido], { type: 'text/csv;charset=utf-8' }))
  enlace.download = nombre
  document.body.appendChild(enlace)
  enlace.click()
  enlace.remove()
  setTimeout(() => URL.revokeObjectURL(enlace.href), 1000)
}

/** Lee un archivo del input como data URL (base64) para enviarlo a la API. */
export function leerArchivo(archivo) {
  return new Promise((resolve, reject) => {
    const lector = new FileReader()
    lector.onload = () => resolve(lector.result)
    lector.onerror = () => reject(new Error('No se pudo leer el archivo.'))
    lector.readAsDataURL(archivo)
  })
}
