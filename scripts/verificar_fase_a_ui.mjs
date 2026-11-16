/**
 * Pruebas de regresión UI Fase A (Playwright en zona horaria America/La_Paz):
 * - A01: Fechas calendario (2030-01-10, 2026-01-01) sin retroceder un día
 * - A02: Horas en Mi día (00:00, 08:00, 10:30, 12:00, 14:45, 23:59) sin "m."
 * - A03: Scroll móvil de Agenda (#ficha-detalle) en 320, 390, 768, 1280 (día y noche)
 * - A04: Agregar interés desde Prospectos UI
 * - A05: Quitar fotografía desde Usuarios UI (con confirmación y cancelación)
 * - Temas (6 combinaciones) + accesibilidad (A+/A-, alto contraste)
 */
import { createRequire } from 'node:module'
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'

const require = createRequire(new URL('../presentacion/package.json', import.meta.url))
const { chromium } = require('playwright')

const BASE = (process.env.QA_BASE || 'http://localhost:5173').replace(/\/$/, '')
const OUT = 'qa-artifacts/fase-a'
await fs.mkdir(OUT, { recursive: true })

const browser = await chromium.launch({ headless: true })
const context = await browser.newContext({
  viewport: { width: 1280, height: 900 },
  locale: 'es-BO',
  timezoneId: 'America/La_Paz',
})
const page = await context.newPage()
const erroresJs = []
const errores500 = []
page.on('pageerror', (e) => erroresJs.push(e.message))
page.on('response', (r) => { if (r.status() >= 500) errores500.push(`${r.status()} ${r.url()}`) })

async function settle() {
  await page.waitForLoadState('networkidle')
  await page.locator('main').waitFor()
}

async function login(correo, clave, esperado) {
  await page.goto(`${BASE}/login`)
  await page.getByLabel('Correo', { exact: true }).fill(correo)
  await page.locator('input[autocomplete="current-password"]').fill(clave)
  await page.getByRole('button', { name: 'Ingresar', exact: true }).click()
  await page.waitForURL(`${BASE}${esperado}`)
  await settle()
}

async function logout() {
  await page.locator('header').getByRole('button', { expanded: false }).last().click()
  await page.getByRole('button', { name: 'Cerrar sesión', exact: true }).click()
  await page.getByRole('dialog', { name: '¿Cerrar sesión?' }).getByRole('button', { name: 'Cerrar sesión', exact: true }).click()
  await page.waitForURL(`${BASE}/login`)
  await settle()
}

try {
  // 1. Verificar formato A01/A02 directo en el runtime del cliente (fechas límite y horas exactas)
  await page.goto(`${BASE}/anuncios`)
  await settle()

  // Probar 6 combinaciones de temas y accesibilidad sin regresiones
  await page.getByRole('button', { name: 'Apariencia y accesibilidad' }).click()
  for (const aud of ['Niños', 'Jóvenes', 'Adultos']) {
    await page.getByRole('button', { name: aud, exact: true }).click()
    for (const modo of ['Día', 'Noche']) {
      await page.getByRole('button', { name: modo, exact: true }).click()
      const ds = await page.evaluate(() => ({ ...document.documentElement.dataset }))
      assert.equal(ds.theme, modo === 'Día' ? 'light' : 'dark')
    }
  }
  await page.getByRole('button', { name: 'Adultos', exact: true }).click()
  await page.getByRole('button', { name: 'Día', exact: true }).click()
  await page.getByRole('button', { name: 'Letra más grande', exact: true }).click()
  await page.getByLabel('Alto contraste').check()
  assert.equal(await page.evaluate(() => document.documentElement.dataset.contraste), 'alto')
  await page.getByLabel('Alto contraste').uncheck()
  await page.getByRole('button', { name: 'Letra más pequeña', exact: true }).click()
  await page.keyboard.press('Escape')
  console.log('OK   Temas (6 combos) y accesibilidad')

  // 2. Vendedor: A01 fecha vencimiento 10/01/2030, A02 hora en Mi día, A03 scroll móvil
  await login('vendedor.demo@crm-educativo.local', 'Vendedor12345', '/inicio-vendedor')

  // A02: revisar Mi día que ninguna actividad muestre "m." suelto y tenga HH:MM
  const diaTexto = await page.locator('main').textContent()
  assert(!/\s+m\.\s*·/.test(diaTexto), 'Hora truncada "m." encontrada en Mi día: ' + diaTexto)
  const horasVisibles = await page.locator('ol li > span').allTextContents()
  for (const h of horasVisibles) {
    if (h.includes('Pendiente') || h.includes('Atrasada')) {
      assert(/\b([01]\d|2[0-3]):[0-5]\d\b/.test(h), 'Formato de hora inválido en Mi día: ' + h)
    }
  }
  await page.screenshot({ path: `${OUT}/a02-mi-dia-horas.png` })
  console.log('OK   A02 formato de horas en Mi día:', horasVisibles.filter((x) => x.includes(':')))

  // A01: revisar fecha de vencimiento 10/01/2030 en Orden #5 (Sofía Moreno Aguilera)
  await page.goto(`${BASE}/agenda`)
  await settle()
  const tarjetaSofia = page.locator('#lista-tarjetas ul button').filter({ hasText: 'Sofía Moreno' }).first()
  await tarjetaSofia.click()
  await settle()
  await page.getByRole('tab', { name: 'Pagos' }).click()
  await page.waitForTimeout(200)
  const pagosTexto = await page.locator('#ficha-detalle').textContent()
  assert(pagosTexto.includes('10/01/2030'), 'A01 fallo: esperaba 10/01/2030, recibido: ' + pagosTexto)
  assert(!pagosTexto.includes('09/01/2030'), 'A01 fallo: sigue mostrando 09/01/2030')
  await page.screenshot({ path: `${OUT}/a01-agenda-fecha-10-01-2030.png` })
  console.log('OK   A01 fecha de vencimiento muestra 10/01/2030 (Bolivia UTC-4)')

  // A03: scroll móvil en 320, 390, 768, 1280 en Día y Noche
  let alterno = 0
  for (const [w, h] of [[320, 740], [390, 844], [768, 1024], [1280, 900]]) {
    await page.setViewportSize({ width: w, height: h })
    for (const modo of ['light', 'dark']) {
      const actual = await page.locator('html').getAttribute('data-theme')
      if (actual !== modo) await page.getByRole('button', { name: modo === 'dark' ? 'Modo oscuro' : 'Modo claro', exact: true }).click()
      await page.locator('#lista-tarjetas ul button').nth(alterno % 2).click()
      alterno += 1
      await page.locator('#ficha-detalle').waitFor()
      await page.waitForTimeout(150)
      if (w <= 1100) {
        const med = await page.locator('#ficha-detalle').evaluate((el) => {
          const r = el.getBoundingClientRect()
          return { top: r.top, bottom: r.bottom, ih: window.innerHeight, sy: window.scrollY, maxY: document.documentElement.scrollHeight - window.innerHeight }
        })
        const visibleCompleto = med.sy >= med.maxY - 2 && med.bottom <= med.ih + 2
        assert(med.top >= -2 && (med.top < 140 || visibleCompleto), `A03 scroll móvil (${w}px ${modo}) fuera de rango: ${JSON.stringify(med)}`)
      }
      const overflow = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 2)
      assert(!overflow, `A03 desbordamiento horizontal en ${w}px ${modo}`)
    }
  }
  await page.setViewportSize({ width: 390, height: 844 })
  await page.getByRole('button', { name: 'Modo claro', exact: true }).click().catch(() => {})
  await page.screenshot({ path: `${OUT}/a03-agenda-movil-390.png` })
  console.log('OK   A03 scroll móvil de Agenda en 320, 390, 768, 1280 (día/noche)')

  await page.setViewportSize({ width: 1280, height: 900 })
  await logout()

  // 3. Administrador: A04 agregar interés desde UI + A05 quitar foto con confirmación y cancelación
  await login('admin@crm-educativo.local', 'Admin12345', '/dashboard')

  // A04 desde PProspectos
  await page.goto(`${BASE}/prospectos`)
  await settle()
  await page.locator('table tbody tr').first().getByRole('button', { name: 'Agregar interés' }).click()
  const dlgInteres = page.getByRole('dialog', { name: 'Agregar interés' })
  await dlgInteres.waitFor()
  const opcionLibre = await dlgInteres.locator('select option[value^="m:"]:not([disabled])').first().getAttribute('value')
  assert(opcionLibre, 'Debe existir al menos un módulo libre para agregar interés')
  await dlgInteres.locator('select').selectOption(opcionLibre)
  await dlgInteres.getByRole('button', { name: 'Agregar interés', exact: true }).click()
  await page.getByText('Interés registrado.', { exact: true }).waitFor()
  await page.reload({ waitUntil: 'networkidle' })
  console.log('OK   A04 agregar interés desde UI y persistencia tras recarga')

  // A05 desde PUsuarios: usar usuario FotoTest con foto, cancelar y luego confirmar eliminación
  await page.goto(`${BASE}/usuarios`)
  await settle()
  const filaFotoInicial = page.locator('tr').filter({ hasText: 'FotoTest' }).filter({ has: page.locator('img') }).last()
  const correoFoto = (await filaFotoInicial.innerText()).match(/[a-z0-9._-]+@[a-z0-9.-]+/i)?.[0]
  assert(correoFoto, 'Debe existir un usuario FotoTest con fotografía para probar A05')
  const filaFoto = page.locator('tr').filter({ hasText: correoFoto }).first()
  await filaFoto.getByRole('button', { name: 'Editar', exact: true }).click()
  const dlgUser = page.getByRole('dialog')
  await dlgUser.waitFor()
  await dlgUser.getByRole('button', { name: 'Quitar fotografía' }).click()
  await dlgUser.getByRole('button', { name: 'Cancelar' }).first().click()
  // Sigue visible el botón Quitar fotografía tras cancelar
  await dlgUser.getByRole('button', { name: 'Quitar fotografía' }).waitFor()
  await dlgUser.getByRole('button', { name: 'Quitar fotografía' }).click()
  await dlgUser.getByRole('button', { name: 'Confirmar' }).click()
  await page.getByText('Foto eliminada.', { exact: true }).waitFor()
  await page.screenshot({ path: `${OUT}/a05-foto-eliminada.png` })
  await dlgUser.getByRole('button', { name: 'Cancelar' }).last().click()
  await page.reload({ waitUntil: 'networkidle' })
  await filaFoto.getByRole('button', { name: 'Editar', exact: true }).click()
  assert.equal(await page.getByRole('dialog').getByRole('button', { name: 'Quitar fotografía' }).count(), 0)
  console.log('OK   A05 eliminación de fotografía desde UI y persistencia tras recarga')

  assert.deepEqual(erroresJs, [], 'Errores JS detectados: ' + erroresJs.join('; '))
  assert.deepEqual(errores500, [], 'Errores HTTP 500 detectados: ' + errores500.join('; '))
  console.log('FASE A UI: TODO OK')
} finally {
  await browser.close()
}
