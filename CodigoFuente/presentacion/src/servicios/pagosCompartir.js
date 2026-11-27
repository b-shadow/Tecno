/** Utilidades simples y centralizadas para compartir enlaces de pago Stripe por WhatsApp, correo o copia manual. */

/** Normaliza teléfonos para wa.me usando prefijo 591 de Bolivia sin duplicarlo. */
export function normalizarTelefonoBolivia(raw) {
  const texto = String(raw || '').trim()
  const digitos = texto.replace(/\D/g, '')
  if (!digitos || digitos.length < 7 || /^0+$/.test(digitos)) {
    return { valido: false, telefono: null, error: 'El prospecto no tiene un número de teléfono válido registrado.' }
  }
  if (digitos.startsWith('591') && digitos.length >= 11) {
    return { valido: true, telefono: digitos, error: null }
  }
  if (digitos.length === 7 || digitos.length === 8) {
    return { valido: true, telefono: `591${digitos}`, error: null }
  }
  if (texto.startsWith('+') && digitos.length >= 10) {
    return { valido: true, telefono: digitos, error: null }
  }
  const sinCero = digitos.replace(/^0+/, '')
  if (sinCero.length === 8) {
    return { valido: true, telefono: `591${sinCero}`, error: null }
  }
  return { valido: true, telefono: digitos, error: null }
}

export function mensajeWhatsAppPago({ prospectoNombre, programa, ordenNro, cuotaNro, totalCuotas, monto, vencimiento, enlace }) {
  const montoTexto = Number(monto || 0).toLocaleString('es-BO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return [
    `Hola, ${prospectoNombre}.`,
    '',
    'Te compartimos el enlace para realizar el pago de tu programa educativo en UNEXO.',
    '',
    `Programa: ${programa}`,
    `Orden: #${ordenNro}`,
    `Cuota: ${cuotaNro} de ${totalCuotas}`,
    `Importe: Bs ${montoTexto}`,
    `Vencimiento: ${vencimiento}`,
    '',
    'Puedes realizar tu pago mediante el siguiente enlace:',
    '',
    enlace,
    '',
    'Operación de demostración mediante Stripe Sandbox.',
    '',
    'Gracias por confiar en UNEXO.',
  ].join('\n')
}

export function mensajeWhatsAppSetup({ prospectoNombre, programa, enlace }) {
  return [
    `Hola, ${prospectoNombre}.`,
    '',
    `Te compartimos el enlace seguro de Stripe Sandbox para registrar tu tarjeta de débito o crédito en UNEXO (${programa}):`,
    '',
    enlace,
    '',
    'Tus datos bancarios se ingresan directamente en Stripe y no se almacenan completos en UNEXO.',
  ].join('\n')
}

export function plantillaCorreoPago({ prospectoNombre, programa, modulo, ordenNro, cuotaNro, totalCuotas, monto, vencimiento, enlace }) {
  const montoTexto = Number(monto || 0).toLocaleString('es-BO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
  return {
    asunto: 'UNEXO — Enlace de pago de tu programa educativo',
    texto_boton: 'Completar pago',
    mensaje: [
      `Hola, ${prospectoNombre}.`,
      '',
      'Te enviamos los detalles y el enlace seguro de Stripe Sandbox para completar tu pago en UNEXO:',
      '',
      `Programa: ${programa}${modulo ? ` — ${modulo}` : ''}`,
      `Orden: #${ordenNro}`,
      `Cuota: ${cuotaNro} de ${totalCuotas}`,
      `Importe: Bs ${montoTexto} (BOB)`,
      `Vencimiento: ${vencimiento}`,
      '',
      'Haz clic en el botón "Completar pago" o abre el enlace incluido en este correo.',
      'Operación de demostración mediante Stripe Sandbox.',
    ].join('\n'),
    enlace,
  }
}

export function plantillaCorreoSetup({ prospectoNombre, programa, enlace }) {
  return {
    asunto: 'UNEXO — Enlace para registrar tu tarjeta',
    texto_boton: 'Registrar tarjeta',
    mensaje: [
      `Hola, ${prospectoNombre}.`,
      '',
      `Puedes registrar de forma segura tu tarjeta de débito o crédito para ${programa} mediante Stripe Sandbox:`,
      '',
      'Haz clic en "Registrar tarjeta" para abrir el formulario oficial de Stripe.',
    ].join('\n'),
    enlace,
  }
}

export function urlWhatsApp(telefonoNormalizado, mensaje) {
  return `https://wa.me/${telefonoNormalizado}?text=${encodeURIComponent(mensaje)}`
}

export async function copiarAlPortapapeles(texto) {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(texto)
      return true
    }
  } catch {
    // Si Clipboard API falla en contexto sin foco o HTTP no local, se recurre a copia manual.
  }
  return false
}
