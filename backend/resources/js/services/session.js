const tokenKey = 'crm_token'
const userKey = 'crm_usuario'

export function clearStoredSession() {
  for (const storage of [localStorage, sessionStorage]) {
    storage.removeItem(tokenKey)
    storage.removeItem(userKey)
  }
}

export function readSession() {
  for (const storage of [sessionStorage, localStorage]) {
    try {
      const token = storage.getItem(tokenKey)
      const usuario = JSON.parse(storage.getItem(userKey) || 'null')
      if (token && usuario) return { token, usuario, remember: storage === localStorage }
    } catch {
      // Una entrada corrupta no debe impedir abrir el formulario de acceso.
    }
    storage.removeItem(tokenKey)
    storage.removeItem(userKey)
  }
  return { token: null, usuario: null, remember: false }
}

export function getStoredToken() {
  return readSession().token
}

export function persistSession(data, remember) {
  clearStoredSession()
  const storage = remember ? localStorage : sessionStorage
  storage.setItem(tokenKey, data.token)
  storage.setItem(userKey, JSON.stringify(data.usuario))
}
