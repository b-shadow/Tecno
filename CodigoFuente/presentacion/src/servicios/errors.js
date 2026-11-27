/** Mensaje util tanto para las validaciones de Laravel como para fallos de red. */
export function apiErrorMessage(error, fallback = 'No se pudo completar la operacion.') {
  const data = error.response?.data
  const fields = data?.errores || data?.errors
  const messages = fields && Object.values(fields).flat().filter((value) => typeof value === 'string')
  if (messages?.length) return [...new Set(messages)].slice(0, 3).join(' ')
  return data?.mensaje || data?.message || fallback
}
