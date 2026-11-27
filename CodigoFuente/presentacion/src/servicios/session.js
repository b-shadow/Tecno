// Sesión guardada en el navegador: el token y los datos que devuelve /login o /me (usuario, menú y permisos).
// "Recordarme" usa localStorage; si no, sessionStorage (se borra al cerrar el navegador).
const tokenKey = 'crm_token'
const userKey = 'crm_usuario'
const menuKey = 'crm_menu'

function almacenes() {
  try {
    return [sessionStorage, localStorage]
  } catch {
    return []
  }
}

function limpiar(storage) {
  try {
    storage.removeItem(tokenKey)
    storage.removeItem(userKey)
    storage.removeItem(menuKey)
  } catch {
    // Almacenamiento bloqueado: no hay nada que limpiar.
  }
}

export function clearStoredSession() {
  almacenes().forEach(limpiar)
}

export function readSession() {
  for (const storage of almacenes()) {
    try {
      const token = storage.getItem(tokenKey)
      const usuario = JSON.parse(storage.getItem(userKey) || 'null')
      const { menu = [], permisos = {} } = JSON.parse(storage.getItem(menuKey) || '{}')
      if (token && usuario) return { token, usuario, menu, permisos, remember: storage === localStorage }
      if (token) limpiar(storage) // token sin usuario: sesión a medias, no se reutiliza
    } catch {
      limpiar(storage) // una entrada corrupta se descarta y no impide abrir el formulario de acceso
    }
  }
  return { token: null, usuario: null, menu: [], permisos: {}, remember: false }
}

export function getStoredToken() {
  return readSession().token
}

export function persistSession(data, remember) {
  clearStoredSession()
  try {
    const storage = remember ? localStorage : sessionStorage
    storage.setItem(tokenKey, data.token)
    storage.setItem(userKey, JSON.stringify(data.usuario))
    storage.setItem(menuKey, JSON.stringify({ menu: data.menu || [], permisos: data.permisos || {} }))
  } catch {
    // Sin almacenamiento la sesión vive solo en memoria hasta recargar.
  }
}
