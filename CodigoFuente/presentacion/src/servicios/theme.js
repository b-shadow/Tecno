import { useSyncExternalStore } from 'react'

/*
 * Apariencia (enunciado 5): público (niños, jóvenes, adultos), día/noche automático según la hora local del dispositivo
 * o manual, tamaño de letra y alto contraste. Se aplica como atributos en <html> y se recuerda en localStorage.
 */
const CLAVE = 'crm_apariencia'
export const DIA_DESDE = 7
export const NOCHE_DESDE = 19

const META_COLORES = {
  adultos: { light: '#083456', dark: '#0b1f33' },
  jovenes: { light: '#7c3aed', dark: '#180f2c' },
  niños: { light: '#dbf0ff', dark: '#172554' },
}

const porDefecto = { modo: 'auto', audiencia: 'adultos', letra: 0, contraste: 'normal' }
let preferencias = { ...porDefecto, ...leer() }
const oyentes = new Set()

function normalizarPreferencias(raw) {
  if (!raw || typeof raw !== 'object') return {}
  // Compatibilidad: migra preferencias guardadas anteriormente como "ninos" o "nino" hacia "niños".
  if (raw.audiencia === 'ninos' || raw.audiencia === 'nino') {
    return { ...raw, audiencia: 'niños' }
  }
  return raw
}

function leer() {
  try {
    const guardado = JSON.parse(localStorage.getItem(CLAVE) || 'null')
    if (guardado) {
      const normalizado = normalizarPreferencias(guardado)
      if (normalizado.audiencia !== guardado.audiencia) {
        localStorage.setItem(CLAVE, JSON.stringify(normalizado))
      }
      return normalizado
    }
    // Compatibilidad con el selector anterior de claro/oscuro.
    const anterior = localStorage.getItem('crm_theme')
    return anterior ? { modo: anterior } : {}
  } catch {
    return {}
  }
}

/** 'light' entre las 07:00 y antes de las 19:00 según el reloj del dispositivo del usuario; 'dark' el resto. */
export function temaPorHora(fecha = new Date()) {
  const hora = fecha.getHours()
  return hora >= DIA_DESDE && hora < NOCHE_DESDE ? 'light' : 'dark'
}

export function temaEfectivo(p = preferencias) {
  return p.modo === 'auto' ? temaPorHora() : p.modo
}

export function aplicar(p = preferencias) {
  const html = document.documentElement
  const modoReal = temaEfectivo(p)
  const audiencia = p.audiencia || 'adultos'
  html.dataset.theme = modoReal
  html.dataset.audiencia = audiencia
  html.dataset.letra = String(p.letra ?? 0)
  if (p.contraste === 'alto') html.dataset.contraste = 'alto'
  else delete html.dataset.contraste

  const meta = (META_COLORES[audiencia] || META_COLORES.adultos)[modoReal]
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', meta)
}

export function cambiar(cambios) {
  preferencias = { ...preferencias, ...cambios }
  try {
    localStorage.setItem(CLAVE, JSON.stringify(preferencias))
  } catch {
    // Sin almacenamiento se aplica solo en esta visita.
  }
  aplicar()
  oyentes.forEach((o) => o())
}

export function useApariencia() {
  return useSyncExternalStore((o) => {
    oyentes.add(o)
    return () => oyentes.delete(o)
  }, () => preferencias)
}

// En modo automático, revisa cada minuto si cambió la hora del dispositivo para alternar día/noche en vivo.
aplicar()
setInterval(() => {
  if (preferencias.modo === 'auto') {
    aplicar()
    oyentes.forEach((o) => o())
  }
}, 60_000)
