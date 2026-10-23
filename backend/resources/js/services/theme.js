import { useSyncExternalStore } from 'react'

/*
 * Apariencia (enunciado 5): público (niños, jóvenes, adultos), día/noche automático según la hora del cliente
 * o manual, tamaño de letra y alto contraste. Se aplica como atributos de <html> y se recuerda en este navegador.
 */
const CLAVE = 'crm_apariencia'
export const DIA_DESDE = 7
export const NOCHE_DESDE = 19

const porDefecto = { modo: 'auto', audiencia: 'adultos', letra: 0, contraste: 'normal' }
let preferencias = { ...porDefecto, ...leer() }
const oyentes = new Set()

function leer() {
  try {
    const guardado = JSON.parse(localStorage.getItem(CLAVE) || 'null')
    // Compatibilidad con el selector anterior de claro/oscuro.
    const anterior = localStorage.getItem('crm_theme')
    return guardado || (anterior ? { modo: anterior } : {})
  } catch {
    return {}
  }
}

/** 'light' entre las 07:00 y las 19:00 del reloj del cliente; 'dark' el resto. */
export function temaPorHora(fecha = new Date()) {
  const hora = fecha.getHours()
  return hora >= DIA_DESDE && hora < NOCHE_DESDE ? 'light' : 'dark'
}

export function temaEfectivo(p = preferencias) {
  return p.modo === 'auto' ? temaPorHora() : p.modo
}

export function aplicar(p = preferencias) {
  const html = document.documentElement
  html.dataset.theme = temaEfectivo(p)
  html.dataset.audiencia = p.audiencia
  html.dataset.letra = String(p.letra)
  if (p.contraste === 'alto') html.dataset.contraste = 'alto'
  else delete html.dataset.contraste
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', html.dataset.theme === 'dark' ? '#0b1f33' : '#083456')
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

// En modo automático, revisa cada minuto si ya cambió de día a noche.
aplicar()
setInterval(() => {
  if (preferencias.modo === 'auto') aplicar()
}, 60_000)
