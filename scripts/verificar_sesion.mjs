// Regresion sin navegador ni dependencias: persistencia, cierre y datos corruptos.
import assert from 'node:assert/strict'
import { apiErrorMessage } from '../presentacion/src/servicios/errors.js'
import { clearStoredSession, getStoredToken, persistSession, readSession } from '../presentacion/src/servicios/session.js'

function storage() {
  const items = new Map()
  return { getItem: (key) => items.get(key) ?? null, setItem: (key, value) => items.set(key, String(value)), removeItem: (key) => items.delete(key) }
}
globalThis.localStorage = storage()
globalThis.sessionStorage = storage()
const data = { token: 'token-ficticio-de-prueba', usuario: { id: 1, rol: 'vendedor' } }
assert.equal(getStoredToken(), null)
persistSession(data, true)
assert.equal(localStorage.getItem('crm_token'), data.token)
assert.equal(sessionStorage.getItem('crm_token'), null)
assert.equal(readSession().remember, true)
persistSession(data, false)
assert.equal(localStorage.getItem('crm_token'), null)
assert.equal(sessionStorage.getItem('crm_token'), data.token)
assert.equal(readSession().remember, false)
assert.deepEqual(readSession().usuario, data.usuario)
persistSession(data, true)
sessionStorage.setItem('crm_token', 'sesion-corrupta')
sessionStorage.setItem('crm_usuario', '{invalido')
assert.equal(getStoredToken(), data.token)
assert.equal(sessionStorage.getItem('crm_token'), null)
clearStoredSession()
assert.equal(getStoredToken(), null)
localStorage.setItem('crm_token', 'token-sin-usuario')
assert.equal(getStoredToken(), null)
assert.equal(localStorage.getItem('crm_token'), null)
console.log('13 comprobaciones de sesion aprobadas.')
assert.equal(apiErrorMessage({response:{data:{errors:{correo:['Correo invalido'],nombre:['Nombre requerido','Correo invalido']}}}}),'Correo invalido Nombre requerido')
assert.equal(apiErrorMessage({response:{data:{errores:{campo:['A','B','C','D']}}}}),'A B C')
assert.equal(apiErrorMessage({response:{data:{mensaje:'Acceso denegado'}}}),'Acceso denegado')
assert.equal(apiErrorMessage({response:{data:{message:'Validation failed'}}}),'Validation failed')
assert.equal(apiErrorMessage(new Error('Network Error'),'Sin conexion'),'Sin conexion')
assert.equal(apiErrorMessage({response:{data:{errors:{campo:[null,12]}}}},'Error util'),'Error util')
console.log('6 comprobaciones de mensajes de error aprobadas.')
