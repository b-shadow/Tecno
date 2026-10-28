// Clases de color que dependen de un dato. Van completas (Tailwind solo genera las clases que ve escritas).
// El color de serie se fija en la variable --c, que las utilidades leen como bg-c, text-c, border-c.

/** Etapas del embudo (RF3.2): estado de la BD → clave de tono. */
export const ETAPA = {
  Nuevo: 'nuevo', 'En Contacto': 'contacto', Seguimiento: 'seguimiento',
  'Promesa de Pago': 'promesa', Convertido: 'convertido', Perdido: 'perdido',
}

export const TONO = {
  nuevo: '[--c:var(--etapa-nuevo)]',
  contacto: '[--c:var(--etapa-contacto)]',
  seguimiento: '[--c:var(--etapa-seguimiento)]',
  promesa: '[--c:var(--etapa-promesa)]',
  convertido: '[--c:var(--etapa-convertido)]',
  perdido: '[--c:var(--etapa-perdido)]',
}

/** Áreas del catálogo: el color de cada programa (1 a 5). */
export const AREA = {
  1: '[--c:var(--programa-1)]',
  2: '[--c:var(--programa-2)]',
  3: '[--c:var(--programa-3)]',
  4: '[--c:var(--programa-4)]',
  5: '[--c:var(--programa-5)]',
}

/** Color del texto de una etiqueta según el estado (embudo, pagos, usuarios, bitácora, notificaciones). */
const EXITO = 'text-exito'
const PELIGRO = 'text-peligro'
const AVISO = 'text-aviso'
const INFO = 'text-etapa-seguimiento'
const COLOR_ESTADO = {
  nuevo: 'text-(--etapa-nuevo)', 'en-contacto': 'text-(--etapa-contacto)', seguimiento: 'text-(--etapa-seguimiento)',
  'promesa-de-pago': 'text-(--etapa-promesa)',
  convertido: EXITO, 'pago-aprobado': EXITO, activo: EXITO, pagada: EXITO, recibida: EXITO,
  perdido: PELIGRO, 'pago-rechazado': PELIGRO, inactivo: PELIGRO, error: PELIGRO, fallida: PELIGRO,
  login_fallido: PELIGRO, acceso_denegado: PELIGRO,
  'en-revision': AVISO, 'pendiente-de-pago': AVISO, pendiente: AVISO, atrasada: AVISO,
  realizada: INFO, exportada: INFO, enviada: INFO, login_exitoso: INFO,
}

/** 'Promesa de Pago' → 'promesa-de-pago' (sin tildes ni mayúsculas, como lo guarda cada tabla). */
const clave = (estado = '') => String(estado).toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/\s+/g, '-')

export const colorEstado = (estado) => COLOR_ESTADO[clave(estado)] || 'text-tinta-suave'
