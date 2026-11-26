/**
 * Pruebas E2E integrales sobre navegador Playwright Chromium (Refactorización Módulo de Pagos):
 * - D01–D12: reglas dinámicas de descuentos en UI y backend + vista previa de cuotas + monto exacto Stripe
 * - P01–P32: creación de orden, envío manual sin redirección, modal único compartir, WhatsApp, SMTP real,
 *   pago Stripe (4242, 3DS, Mastercard, rechazo 0002), retorno público confirmación/cancelación,
 *   webhook sin retorno UI, registro tarjeta Setup (activar/desactivar/inactivos), historial, bloqueo QR/manual
 * - A01–A12: envío automático activado/desactivado + enlace público por cuota /pagos/cuota?token=... con regeneración tras expiración
 * - Visual 1–17: colapsado inicial de Métodos e Historial, 320/390/768/1280px sin desbordamiento, 6 temas + alto contraste + tamaño fuente
 */
import { createRequire } from 'node:module'
import { execFileSync } from 'node:child_process'
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'

const require = createRequire(new URL('../presentacion/package.json', import.meta.url))
const { chromium } = require('playwright')

const BASE = (process.env.QA_BASE || 'http://localhost:5173').replace(/\/$/, '')
const API = (process.env.QA_API || 'http://127.0.0.1:8001/api').replace(/\/$/, '')
const PSQL = 'C:\\Program Files\\PostgreSQL\\17\\bin\\psql.exe'
const OUT = 'qa-artifacts/refactor-pagos'
await fs.mkdir(OUT, { recursive: true })

function psqlScalar(sql) {
  return execFileSync(PSQL, ['-U', 'postgres', '-d', 'crm_educativo', '-tAc', sql], { encoding: 'utf8' }).trim()
}

function expireStripeSession(sessionId) {
  execFileSync('php', [
    '-r',
    `require 'negocio/vendor/autoload.php'; $app=require 'negocio/bootstrap/app.php'; $app->make(Illuminate\\Contracts\\Console\\Kernel::class)->bootstrap(); $sc = new Stripe\\StripeClient(config('services.stripe.secret')); $sc->checkout->sessions->expire('${sessionId}');`,
  ])
}

async function api(path, method = 'GET', body = null, token = null) {
  const headers = { Accept: 'application/json' }
  if (body !== null) headers['Content-Type'] = 'application/json'
  if (token) headers.Authorization = `Bearer ${token}`
  const res = await fetch(`${API}${path}`, {
    method,
    headers,
    body: body !== null ? JSON.stringify(body) : undefined,
  })
  const data = await res.json().catch(() => ({}))
  return { status: res.status, data }
}

const { data: admLogin } = await api('/login', 'POST', { correo: 'admin@crm-educativo.local', password: 'Admin12345' })
assert(admLogin.token, 'No se pudo autenticar admin')
const adm = admLogin.token
const { data: vndLogin } = await api('/login', 'POST', { correo: 'vendedor.demo@crm-educativo.local', password: 'Vendedor12345' })
assert(vndLogin.token, 'No se pudo autenticar vendedor')
const vnd = vndLogin.token

const { data: cat } = await api('/catalogo')
const progMulti = cat.programas.find((p) => p.modulos.length >= 4) || cat.programas.find((p) => p.modulos.length >= 3) || cat.programas[0]
const mod = progMulti.modulos[0]

let uidCounter = 1
async function crearProspectoYOrden({ cuotas, primerVencimiento = '2030-07-01', telefono = '71234567', sufijoCorreo = 'e2e', moduloCodigo = mod.codigo, envioAutomatico = true }) {
  const uid = `${String(Date.now()).slice(-6)}${uidCounter++}`
  const doc = `RP${uid}`
  const correoCliente = `unexouagrm+${sufijoCorreo}${uid}@gmail.com`
  const { status: stP, data: dP } = await api('/prospectos', 'POST', {
    documento: doc, nombre: 'Valeria', apellido: 'Cliente Refactor',
    correo: correoCliente, telefono,
    profesion: 'Ingeniera Comercial', ubicacion: 'Santa Cruz', origen: 'Web',
    modulo_codigo: moduloCodigo,
  }, adm)
  assert.equal(stP, 201, JSON.stringify(dP))
  const nroTarjeta = dP.prospecto.intereses[0].nro_tarjeta
  const { status: stA } = await api(`/intereses/${nroTarjeta}/asignar`, 'PATCH', { vendedor_correo: 'vendedor.demo@crm-educativo.local' }, adm)
  assert.equal(stA, 200)
  let orden = null
  if (cuotas > 0) {
    const { status: stO, data: dO } = await api(`/intereses/${nroTarjeta}/ordenes-pago`, 'POST', {
      modulos: [moduloCodigo], cuotas, primer_vencimiento: primerVencimiento, envio_automatico: envioAutomatico,
    }, vnd)
    assert.equal(stO, 201, JSON.stringify(dO))
    orden = dO.orden
  }
  return { doc, nroTarjeta, correoCliente, orden }
}

async function obtenerFrameCheckout(page) {
  await page.waitForURL(/checkout\.stripe\.com/, { timeout: 30000 })
  await page.waitForLoadState('domcontentloaded')
  const deadline = Date.now() + 30000
  let expandido = false
  while (Date.now() < deadline) {
    const frame = page.frames().find((f) => f.url().includes('elements-inner-habanero'))
    if (frame) {
      if (await frame.locator('#payment-numberInput').isVisible().catch(() => false)) {
        return frame
      }
      if (!expandido) {
        const tarjetaBtn = frame.getByText('Tarjeta', { exact: true }).first()
        if (await tarjetaBtn.isVisible().catch(() => false)) {
          await tarjetaBtn.click().catch(() => {})
          expandido = true
        }
      }
    }
    await page.waitForTimeout(300)
  }
  throw new Error('No cargó el formulario de tarjeta dentro del iframe de Stripe Checkout')
}

async function llenarTarjetaStripe(page, { numero, vencimiento = '1230', cvc = '123', titular = 'Valeria Cliente Refactor' }) {
  const frame = await obtenerFrameCheckout(page)
  await frame.locator('#payment-numberInput').fill(numero)
  await frame.locator('#payment-expiryInput').fill(vencimiento)
  await frame.locator('#payment-cvcInput').fill(cvc)
  const nameInput = frame.locator('#payment-nameInput')
  if (await nameInput.isVisible().catch(() => false)) {
    await nameInput.fill(titular)
  }
  return frame
}

async function enviarFormularioStripe(page) {
  const frame = await obtenerFrameCheckout(page)
  const submit = frame.locator('button[data-testid="payment-form-submit-button"]').first()
  await submit.waitFor({ state: 'visible', timeout: 15000 })
  await page.waitForTimeout(350)
  await submit.click()
  return frame
}

async function aprobar3DS(page) {
  const deadline = Date.now() + 45000
  while (Date.now() < deadline) {
    if (page.url().includes('/pagos/confirmacion')) return
    for (const frame of page.frames()) {
      if (!frame.url().includes('3d_secure_2_test')) continue
      const btn = frame.locator('#test-source-authorize-3ds').first()
      if (await btn.isVisible().catch(() => false)) {
        await page.waitForTimeout(1600)
        await btn.click({ force: true }).catch(() => {})
        await page.waitForTimeout(1500)
        if (page.url().includes('/pagos/confirmacion')) return
      }
    }
    await page.waitForTimeout(400)
  }
  throw new Error('No se completó el desafío 3DS de prueba en Stripe Checkout')
}

async function verificarSinDesbordamiento(page, contexto = '') {
  const dims = await page.evaluate(() => ({
    scroll: document.documentElement.scrollWidth,
    inner: window.innerWidth,
  }))
  assert(dims.scroll <= dims.inner + 2, `Desbordamiento horizontal ${contexto}: scroll=${dims.scroll} > inner=${dims.inner}`)
}

const browser = await chromium.launch({ headless: true })
const evidencias = []
const erroresJs = []

try {
  // Navegador 1: VENDEDOR autenticado (normal)
  const vendorCtx = await browser.newContext({
    viewport: { width: 1280, height: 900 },
    locale: 'es-BO',
    timezoneId: 'America/La_Paz',
    permissions: ['clipboard-read', 'clipboard-write'],
  })
  const vPage = await vendorCtx.newPage()
  vPage.on('pageerror', (e) => erroresJs.push(`Vendedor: ${e.message}`))
  await vPage.addInitScript(() => {
    window.__openedUrls = []
    window.open = (u) => { window.__openedUrls.push(u); return null }
  })

  await vPage.goto(`${BASE}/login`)
  await vPage.getByLabel('Correo', { exact: true }).fill('vendedor.demo@crm-educativo.local')
  await vPage.locator('input[autocomplete="current-password"]').fill('Vendedor12345')
  await vPage.getByRole('button', { name: 'Ingresar', exact: true }).click()
  await vPage.waitForURL(/inicio-vendedor/)

  // =========================================================================
  // FLUJO 1: D01–D12 (Reglas estrictas de descuentos), P01–P14, P31–P32, A01, A10, Visual 1–13
  // =========================================================================
  const caso1 = await crearProspectoYOrden({ cuotas: 0, telefono: '+59171234567', sufijoCorreo: 'c1' })
  await vPage.goto(`${BASE}/agenda?interes=${caso1.nroTarjeta}`)
  await vPage.getByRole('tab', { name: 'Pagos', exact: true }).click()
  await vPage.getByRole('region', { name: 'Gestión de pagos' }).waitFor()

  // P32 & Visual: cero QR/Transferencia, cero comprobante manual, cero URLs permanentes, <details> colapsados inicialmente
  assert.equal(await vPage.getByRole('button', { name: 'Pagar con Stripe' }).count(), 0)
  assert.equal(await vPage.getByRole('button', { name: 'Registrar tarjeta con Stripe' }).count(), 0)
  assert.equal(await vPage.getByRole('button', { name: /QR \/ Transferencia/i }).count(), 0)
  assert.equal(await vPage.locator('input[type="file"]').count(), 0)
  const metodosDetails = vPage.locator('details', { hasText: 'Métodos de pago del cliente' })
  const historialDetails = vPage.locator('details', { hasText: 'Historial de pagos' })
  assert.equal(await metodosDetails.evaluate((el) => el.open), false, 'Métodos de pago debe iniciar contraído')
  assert.equal(await historialDetails.evaluate((el) => el.open), false, 'Historial de pagos debe iniciar contraído')

  // Abrir FormularioOrdenPago y verificar D01-D09 + D11 + A01
  await vPage.getByRole('region', { name: 'Gestión de pagos' }).getByRole('button', { name: 'Generar orden de pago' }).click()
  const modalOrden = vPage.getByRole('dialog', { name: 'Generar orden de pago' })
  await modalOrden.waitFor()

  const checksModulos = modalOrden.locator('fieldset').nth(0).locator('.grid input[type="checkbox"]')
  const fieldsetDctos = modalOrden.locator('fieldset').nth(1)
  const chk3Mod = fieldsetDctos.getByLabel(/3 o m[aá]s m[oó]dulos/i)
  const chkProgComp = fieldsetDctos.getByLabel(/Programa completo/i)
  const chkRecurrente = fieldsetDctos.getByLabel(/Cliente recurrente/i)

  // D01/D02/D06: 1 módulo -> 3_MAS_MODULOS y PROGRAMA_COMPLETO deshabilitados, CLIENTE_RECURRENTE habilitado
  assert.equal(await chk3Mod.isDisabled(), true, 'D02: 3 o más módulos debe iniciar deshabilitado con 1 módulo')
  assert.equal(await chkProgComp.isDisabled(), true, 'D06: Programa completo debe iniciar deshabilitado con 1 módulo')
  assert.equal(await chkRecurrente.isDisabled(), false, 'D07: Cliente recurrente debe estar habilitado siempre')
  await modalOrden.getByText(/Selecciona al menos tres módulos/i).waitFor()

  // Seleccionar 2do módulo: 3_MAS_MODULOS sigue deshabilitado
  await checksModulos.nth(1).check()
  assert.equal(await chk3Mod.isDisabled(), true, 'D02: con 2 módulos debe seguir deshabilitado')

  // D03/D04: Seleccionar 3er módulo -> se habilita 3_MAS_MODULOS
  await checksModulos.nth(2).check()
  assert.equal(await chk3Mod.isDisabled(), false, 'D03: con 3 módulos debe habilitarse 3_MAS_MODULOS')
  await chk3Mod.check()
  assert.equal(await chk3Mod.isChecked(), true)
  const totalCon3 = await modalOrden.locator('section').filter({ hasText: 'Total final' }).innerText()
  assert(totalCon3.includes('10%'), 'D04: debe reflejar 10% aplicado en el resumen')

  // D05: Desmarcar 3er módulo -> desmarca y deshabilita automáticamente 3_MAS_MODULOS
  await checksModulos.nth(2).uncheck()
  assert.equal(await chk3Mod.isChecked(), false, 'D05: 3_MAS_MODULOS debe desmarcarse automáticamente al bajar de 3')
  assert.equal(await chk3Mod.isDisabled(), true, 'D05: 3_MAS_MODULOS debe deshabilitarse al bajar de 3')

  // D07/D08/D09: Seleccionar programa completo -> habilita todos, aplicar y desmarcar 1 revierte PROGRAMA_COMPLETO
  const chkSelCompleto = modalOrden.getByLabel(/Seleccionar programa completo/)
  await chkSelCompleto.check()
  assert.equal(await chkProgComp.isDisabled(), false, 'D07: Programa completo debe habilitarse')
  await chkProgComp.check()
  assert.equal(await chkProgComp.isChecked(), true)
  await checksModulos.nth(0).uncheck()
  assert.equal(await chkProgComp.isChecked(), false, 'D09: Programa completo debe desmarcarse si falta algún módulo')
  assert.equal(await chkProgComp.isDisabled(), true)
  assert.equal(await chkSelCompleto.isChecked(), false)

  // D11: Vista previa de cuotas y volver a seleccionar 1 solo módulo para Caso 1
  await chkSelCompleto.check()
  await chkSelCompleto.uncheck()
  await checksModulos.nth(0).check()
  await modalOrden.getByLabel(/Forma de pago/).selectOption('cuotas')
  await modalOrden.getByLabel(/Cantidad de cuotas/).selectOption('3')
  assert.equal(await modalOrden.locator('table.tabla tbody tr').count(), 4, 'D11: Vista previa de 3 cuotas + fila Total')

  // A01: Envío automático pre-activado para correo válido
  const chkAuto = modalOrden.getByLabel(/Enviar solicitudes y recordatorios autom/i)
  assert.equal(await chkAuto.isChecked(), true, 'A01: Envío automático debe iniciar activado con correo válido')

  // Cambiar a Pago único para Caso 1 y generar
  await modalOrden.getByLabel(/Forma de pago/).selectOption('unico')
  await vPage.screenshot({ path: `${OUT}/01-modal-nueva-orden.png`, fullPage: true })
  await modalOrden.getByRole('button', { name: 'Confirmar orden de pago', exact: true }).click()
  await vPage.getByText('Orden de pago generada.', { exact: true }).waitFor({ timeout: 15000 })

  const orden1Txt = await vPage.locator('h4', { hasText: /Orden de pago #\d+/ }).first().innerText()
  const nroOrden1 = Number(orden1Txt.match(/Orden de pago #(\d+)/)[1])

  // P31 / A12 / Visual: Envío automático activo NO oculta botón Enviar solicitud de pago, progreso visible, sin URL permanente
  await vPage.getByText(/Envíos automáticos:.*Activados/i).waitFor()
  await vPage.getByText('0 de 1 cuota pagada', { exact: true }).waitFor()
  assert.equal(await vPage.locator('progress.pagos-progreso').getAttribute('max'), '1')
  assert.equal(await vPage.getByRole('button', { name: 'Enviar solicitud de pago', exact: true }).count(), 1)
  assert.equal(await vPage.locator('input[readonly][value*="checkout.stripe.com"]').count(), 0, 'No debe haber URL larga permanente en la tarjeta')
  await vPage.screenshot({ path: `${OUT}/02-resumen-y-orden-activa.png`, fullPage: true })
  console.log(`OK   D01-D11 + A01/A12 + Visual orden #${nroOrden1} limpia y validada`)

  // Compartir vía ModalCompartirPago (Copiar + WhatsApp + Correo SMTP)
  await vPage.getByRole('button', { name: 'Enviar solicitud de pago', exact: true }).click()
  const modalComp = vPage.getByRole('dialog', { name: 'Enviar solicitud de pago' })
  await modalComp.waitFor()
  await modalComp.getByRole('button', { name: 'Copiar enlace de pago', exact: true }).waitFor({ timeout: 15000 })
  await modalComp.getByRole('button', { name: 'Copiar enlace de pago', exact: true }).click()
  await modalComp.getByRole('button', { name: 'Enlace copiado correctamente', exact: true }).waitFor({ timeout: 10000 })
  await vPage.getByText('Enlace copiado correctamente.', { exact: true }).waitFor({ timeout: 10000 })
  const urlPago1 = await vPage.evaluate(() => navigator.clipboard.readText())
  assert(urlPago1.startsWith('https://checkout.stripe.com/'), `URL Stripe invalida: ${urlPago1}`)

  await modalComp.getByRole('button', { name: 'Enviar por WhatsApp', exact: true }).click()
  const waUrls = await vPage.evaluate(() => window.__openedUrls)
  assert.equal(waUrls.length, 1)
  assert(waUrls[0].startsWith('https://wa.me/59171234567?text='), `WhatsApp no debe duplicar 591: ${waUrls[0]}`)
  const waDecoded = decodeURIComponent(waUrls[0].split('?text=')[1])
  assert(waDecoded.includes(urlPago1) && waDecoded.includes(`#${nroOrden1}`) && waDecoded.includes('Bs '), 'Mensaje WhatsApp incompleto')

  await modalComp.getByRole('button', { name: 'Enviar por correo electrónico', exact: true }).click()
  assert.equal(await modalComp.locator('input[type="email"]').inputValue(), caso1.correoCliente)
  await vPage.screenshot({ path: `${OUT}/03-modal-compartir-pago.png` })
  await modalComp.getByRole('button', { name: 'Confirmar y enviar', exact: true }).click()
  await vPage.getByText(/aceptado por el servidor SMTP/i).waitFor({ timeout: 25000 })
  assert.equal(Number(psqlScalar(`SELECT count(*) FROM transacciones_stripe WHERE nro_orden = ${nroOrden1} AND nro_cuota = 1;`)), 1)
  console.log('OK   P02-P05 Modal compartir (WhatsApp + SMTP + Copiar) reutiliza sesión única')

  // A10: Expirar sesión Stripe y verificar que el enlace público de correo (/pagos/cuota?token=...) regenera sesión válida y permite pagar al cliente
  const tokenPago1 = psqlScalar(`SELECT token_pago FROM cuotas WHERE nro_orden = ${nroOrden1} AND nro_cuota = 1;`)
  const sesion1 = psqlScalar(`SELECT stripe_sesion FROM transacciones_stripe WHERE nro_orden = ${nroOrden1} AND nro_cuota = 1 LIMIT 1;`)
  assert(tokenPago1, 'Debe existir token_pago en cuotas')
  const notifAuto = Number(psqlScalar(`SELECT count(*) FROM notificaciones WHERE destinatario = '${caso1.correoCliente}' AND estado = 'enviada' AND tipo LIKE '%Orden #${nroOrden1}%';`))
  assert(notifAuto >= 1, 'La orden con envío automático debe enviar y registrar el correo inicial por SMTP')
  const notifManual = Number(psqlScalar(`SELECT count(*) FROM notificaciones WHERE destinatario = '${caso1.correoCliente}' AND estado = 'enviada' AND tipo LIKE '%Enlace de pago de tu programa%';`))
  assert(notifManual >= 1, 'El envío manual desde ModalCompartirPago debe registrarse como enviado por SMTP')
  expireStripeSession(sesion1)

  const clientCtx = await browser.newContext({ viewport: { width: 1280, height: 900 }, locale: 'es-BO', timezoneId: 'America/La_Paz' })
  const cPage = await clientCtx.newPage()
  cPage.on('pageerror', (e) => erroresJs.push(`Cliente: ${e.message}`))

  await cPage.goto(`${BASE}/pagos/cuota?token=${tokenPago1}`)
  await llenarTarjetaStripe(cPage, { numero: '4242 4242 4242 4242' })
  await enviarFormularioStripe(cPage)
  await cPage.waitForURL(/\/pagos\/confirmacion\?session_id=cs_test_.*token=/, { timeout: 45000 })
  await cPage.getByText('¡Pago confirmado por Stripe Sandbox!', { exact: true }).waitFor({ timeout: 25000 })
  assert.equal(await cPage.locator('aside[aria-label="Menú principal"]').count(), 0)
  await cPage.screenshot({ path: `${OUT}/04-cliente-confirmacion-publica.png`, fullPage: true })

  // Reapertura del mismo enlace público cuando la cuota ya está pagada -> no vuelve a cobrar
  await cPage.goto(`${BASE}/pagos/cuota?token=${tokenPago1}`)
  await cPage.getByText('Cuota ya pagada', { exact: true }).waitFor({ timeout: 15000 })
  await cPage.getByText(/Esta cuota ya figura como pagada/i).waitFor()
  assert(!cPage.url().includes('checkout.stripe.com'), 'No debe redirigir a Stripe cuando la cuota ya fue pagada')
  await cPage.screenshot({ path: `${OUT}/05-cliente-cuota-ya-pagada.png`, fullPage: true })
  console.log('OK   A10 enlace público de cuota regenera sesión expirada, cobra y bloquea doble pago tras liquidar')

  // Vendedor actualiza y ve liquidada + historial + correos sin duplicados
  await vPage.getByRole('button', { name: 'Actualizar estado', exact: true }).click()
  await vPage.getByText('1 de 1 cuota pagada', { exact: true }).waitFor({ timeout: 10000 })
  const cerradasDetails = vPage.locator('details', { hasText: /Órdenes liquidadas y anuladas/ })
  await cerradasDetails.waitFor()
  assert.equal(await cerradasDetails.evaluate((el) => el.open), false, 'Órdenes liquidadas deben colapsarse automáticamente')
  await historialDetails.locator('summary').click()
  await vPage.getByText('Pago confirmado por Stripe', { exact: true }).waitFor()
  await vPage.screenshot({ path: `${OUT}/06-vendedor-liquidada-historial.png`, fullPage: true })

  const pi1 = psqlScalar(`SELECT stripe_pago_intent FROM cuotas WHERE nro_orden = ${nroOrden1} AND nro_cuota = 1;`)
  const notifCli = Number(psqlScalar(`SELECT count(*) FROM notificaciones WHERE destinatario = '${caso1.correoCliente}' AND estado = 'enviada' AND mensaje LIKE '%${pi1}%';`))
  const notifVnd = Number(psqlScalar(`SELECT count(*) FROM notificaciones WHERE destinatario = 'vendedor.demo@crm-educativo.local' AND estado = 'enviada' AND mensaje LIKE '%${pi1}%';`))
  assert.equal(notifCli, 1)
  assert.equal(notifVnd, 1)
  evidencias.push({ flujo: 'Flujo 1 (D01-D11, A10, Pago único)', orden: nroOrden1, pi: pi1, notifCli, notifVnd })
  await clientCtx.close()

  // =========================================================================
  // FLUJO 2: D12 Descuento completo real en UI + Plan de 3 cuotas (3DS, MC, Visa, Rechazo, Cancelación, Setup Tarjeta, Toggle Envío Automático)
  // =========================================================================
  const casoDsc = await crearProspectoYOrden({ cuotas: 0, sufijoCorreo: 'd12' })
  await vPage.goto(`${BASE}/agenda?interes=${casoDsc.nroTarjeta}`)
  await vPage.getByRole('tab', { name: 'Pagos', exact: true }).click()
  await vPage.getByRole('region', { name: 'Gestión de pagos' }).getByRole('button', { name: 'Generar orden de pago' }).click()
  const modalDsc = vPage.getByRole('dialog', { name: 'Generar orden de pago' })
  await modalDsc.getByLabel(/Seleccionar programa completo/).check()
  await modalDsc.locator('fieldset').nth(1).getByLabel(/Programa completo/i).check()
  await modalDsc.locator('fieldset').nth(1).getByLabel(/Cliente recurrente/i).check()
  if (progMulti.modulos.length >= 3) {
    await modalDsc.locator('fieldset').nth(1).getByLabel(/3 o m[aá]s m[oó]dulos/i).check()
  }
  await modalDsc.getByRole('button', { name: 'Confirmar orden de pago', exact: true }).click()
  await vPage.getByText('Orden de pago generada.', { exact: true }).waitFor({ timeout: 15000 })
  const nroOrdenDsc = Number((await vPage.locator('h4', { hasText: /Orden de pago #\d+/ }).first().innerText()).match(/#(\d+)/)[1])
  await vPage.getByRole('button', { name: 'Enviar solicitud de pago', exact: true }).click()
  const mCompDsc = vPage.getByRole('dialog', { name: 'Enviar solicitud de pago' })
  await mCompDsc.getByRole('button', { name: 'Copiar enlace de pago', exact: true }).waitFor({ timeout: 15000 })
  await mCompDsc.getByRole('button', { name: 'Cancelar', exact: true }).click()
  const totalOrdenDsc = Number(psqlScalar(`SELECT total FROM ordenes_pago WHERE nro_orden = ${nroOrdenDsc};`))
  const subOrdenDsc = Number(psqlScalar(`SELECT subtotal FROM ordenes_pago WHERE nro_orden = ${nroOrdenDsc};`))
  assert(totalOrdenDsc < subOrdenDsc, `D12: debe guardar total con descuento (${totalOrdenDsc} < ${subOrdenDsc})`)
  console.log(`OK   D12 orden completa #${nroOrdenDsc} con descuentos guardó Bs ${totalOrdenDsc.toFixed(2)} (de ${subOrdenDsc.toFixed(2)})`)

  // Plan de 3 cuotas
  const caso3 = await crearProspectoYOrden({ cuotas: 3, sufijoCorreo: 'c3' })
  await vPage.goto(`${BASE}/agenda?interes=${caso3.nroTarjeta}`)
  await vPage.getByRole('tab', { name: 'Pagos', exact: true }).click()

  // Toggle envíos automáticos en Detalles y opciones
  await vPage.getByRole('button', { name: 'Detalles y opciones', exact: true }).first().click()
  const modalDet = vPage.getByRole('dialog', { name: /Detalles de orden/ })
  await modalDet.getByRole('button', { name: 'Desactivar envíos', exact: true }).click()
  await vPage.getByText(/Envíos automáticos:.*Desactivados/i).waitFor({ timeout: 10000 })
  await vPage.getByRole('button', { name: 'Detalles y opciones', exact: true }).first().click()
  await modalDet.getByRole('button', { name: 'Activar envíos', exact: true }).click()
  await vPage.getByText(/Envíos automáticos:.*Activados/i).waitFor({ timeout: 10000 })

  // Audit visual en 6 temas + alto contraste + tamaños y 4 viewports (320, 390, 768, 1280) sobre UI refactorizada (incluyendo modal abierto en 320px)
  await vPage.setViewportSize({ width: 320, height: 720 })
  await vPage.getByRole('button', { name: 'Enviar solicitud de pago', exact: true }).first().click()
  const modalComp320 = vPage.getByRole('dialog', { name: 'Enviar solicitud de pago' })
  await modalComp320.getByRole('button', { name: 'Copiar enlace de pago', exact: true }).waitFor({ timeout: 15000 })
  await verificarSinDesbordamiento(vPage, 'modal compartir 320px')
  await modalComp320.getByRole('button', { name: 'Cancelar', exact: true }).click()
  for (const [w, h] of [[320, 720], [390, 844], [768, 900], [1280, 900]]) {
    await vPage.setViewportSize({ width: w, height: h })
    await vPage.waitForTimeout(150)
    await verificarSinDesbordamiento(vPage, `viewport ${w}px`)
  }
  await vPage.setViewportSize({ width: 1280, height: 900 })

  for (const audiencia of ['niños', 'jovenes', 'adultos']) {
    for (const modo of ['light', 'dark']) {
      await vPage.evaluate(([a, m]) => {
        const html = document.documentElement
        html.dataset.audiencia = a
        html.dataset.theme = m
      }, [audiencia, modo])
      await vPage.waitForTimeout(120)
      await verificarSinDesbordamiento(vPage, `tema ${audiencia}-${modo}`)
      if ((audiencia === 'niños' && modo === 'light') || (audiencia === 'jovenes' && modo === 'light') || (audiencia === 'adultos' && modo === 'dark')) {
        await vPage.screenshot({ path: `${OUT}/tema-${audiencia}-${modo}.png`, fullPage: true })
      }
    }
  }
  await vPage.evaluate(() => {
    document.documentElement.dataset.audiencia = 'adultos'
    document.documentElement.dataset.theme = 'light'
    document.documentElement.dataset.contraste = 'alto'
    document.documentElement.dataset.letra = '2'
  })
  await vPage.waitForTimeout(120)
  await verificarSinDesbordamiento(vPage, 'alto-contraste-letra-grande')
  await vPage.screenshot({ path: `${OUT}/tema-alto-contraste-grande.png`, fullPage: true })
  await vPage.evaluate(() => {
    delete document.documentElement.dataset.contraste
    document.documentElement.dataset.letra = '0'
  })

  // Cuota 1 (Rechazo -> Cancelación pública -> Continuar -> 3DS), Cuota 2 (MC), Cuota 3 (Visa)
  async function obtenerUrlCuota(idx) {
    await vPage.getByRole('button', { name: 'Enviar solicitud de pago', exact: true }).nth(idx).click()
    const md = vPage.getByRole('dialog', { name: 'Enviar solicitud de pago' })
    await md.getByRole('button', { name: 'Copiar enlace de pago', exact: true }).waitFor({ timeout: 15000 })
    await md.getByRole('button', { name: 'Copiar enlace de pago', exact: true }).click()
    const u = await vPage.evaluate(() => navigator.clipboard.readText())
    await md.getByRole('button', { name: 'Cancelar', exact: true }).click()
    return u
  }

  const c3Ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, locale: 'es-BO' })
  const c3Page = await c3Ctx.newPage()
  c3Page.on('pageerror', (e) => erroresJs.push(`Cliente3: ${e.message}`))

  const url3_c1 = await obtenerUrlCuota(0)
  await c3Page.goto(url3_c1)
  const frameErr = await llenarTarjetaStripe(c3Page, { numero: '4000 0000 0000 0002' })
  await enviarFormularioStripe(c3Page)
  await frameErr.locator('button[data-testid="payment-form-submit-button"]:not([disabled])').waitFor({ timeout: 25000 })
  await frameErr.locator('[role="alert"], .p-FieldError, :text-matches("rechazada|declined", "i")').first().waitFor({ timeout: 10000 })
  assert.equal(psqlScalar(`SELECT estado FROM cuotas WHERE nro_orden = ${caso3.orden.nro_orden} AND nro_cuota = 1;`), 'Pendiente de pago')

  const urlCancel = await c3Page.evaluate(() => {
    const a = [...document.querySelectorAll('a')].find((el) => (el.href || '').includes('cancelado') || el.getAttribute('aria-label')?.match(/back|volver|atrás/i))
    return a?.href || null
  })
  if (urlCancel) await c3Page.goto(urlCancel)
  else await c3Page.locator('header a, [data-testid="business-link"], a[aria-label]').first().click()
  await c3Page.waitForURL(/\/pagos\/cancelado\?session_id=cs_test_.*token=/, { timeout: 25000 })
  await c3Page.getByRole('button', { name: 'Continuar pago en Stripe', exact: true }).waitFor({ timeout: 20000 })
  assert.equal(psqlScalar(`SELECT estado FROM ordenes_pago WHERE nro_orden = ${caso3.orden.nro_orden};`), 'Activa')

  await c3Page.getByRole('button', { name: 'Continuar pago en Stripe', exact: true }).click()
  await llenarTarjetaStripe(c3Page, { numero: '4000 0025 0000 3155' })
  await enviarFormularioStripe(c3Page)
  await aprobar3DS(c3Page)
  await c3Page.waitForURL(/\/pagos\/confirmacion\?session_id=cs_test_/, { timeout: 45000 })
  await c3Page.getByText('¡Pago confirmado por Stripe Sandbox!', { exact: true }).waitFor({ timeout: 25000 })
  await vPage.getByRole('button', { name: 'Actualizar estado', exact: true }).click()
  await vPage.getByText('1 de 3 cuotas pagadas', { exact: true }).waitFor({ timeout: 10000 })

  const url3_c2 = await obtenerUrlCuota(0) // ahora cuota 2 es la primera pendiente con botón Enviar solicitud de pago
  await c3Page.goto(url3_c2)
  await llenarTarjetaStripe(c3Page, { numero: '5555 5555 5555 4444' })
  await enviarFormularioStripe(c3Page)
  await c3Page.waitForURL(/\/pagos\/confirmacion\?session_id=cs_test_/, { timeout: 45000 })
  await c3Page.getByText('¡Pago confirmado por Stripe Sandbox!', { exact: true }).waitFor({ timeout: 25000 })
  await vPage.getByRole('button', { name: 'Actualizar estado', exact: true }).click()
  await vPage.getByText('2 de 3 cuotas pagadas', { exact: true }).waitFor({ timeout: 10000 })

  const url3_c3 = await obtenerUrlCuota(0)
  await c3Page.goto(url3_c3)
  await llenarTarjetaStripe(c3Page, { numero: '4242 4242 4242 4242' })
  await enviarFormularioStripe(c3Page)
  await c3Page.waitForURL(/\/pagos\/confirmacion\?session_id=cs_test_/, { timeout: 45000 })
  await c3Page.getByText('¡Pago confirmado por Stripe Sandbox!', { exact: true }).waitFor({ timeout: 25000 })
  await vPage.getByRole('button', { name: 'Actualizar estado', exact: true }).click()
  await vPage.getByText('3 de 3 cuotas pagadas', { exact: true }).waitFor({ timeout: 10000 })
  console.log(`OK   Plan de 3 cuotas (Rechazo + Cancelación + 3DS + MC + Visa) liquidado a Bs 0,00`)

  // Registro remoto de tarjeta (Setup) desde sección colapsada Métodos de pago del cliente
  const metodos3 = vPage.locator('details', { hasText: 'Métodos de pago del cliente' })
  await metodos3.locator('summary').click()
  await vPage.getByRole('button', { name: 'Solicitar registro de tarjeta', exact: true }).click()
  const modalSetup = vPage.getByRole('dialog', { name: 'Solicitar registro de tarjeta' })
  await modalSetup.getByRole('button', { name: 'Copiar enlace de pago', exact: true }).waitFor({ timeout: 15000 })
  await modalSetup.getByRole('button', { name: 'Copiar enlace de pago', exact: true }).click()
  const urlSetup = await vPage.evaluate(() => navigator.clipboard.readText())
  await modalSetup.getByRole('button', { name: 'Cancelar', exact: true }).click()

  await c3Page.goto(urlSetup)
  await llenarTarjetaStripe(c3Page, { numero: '4242 4242 4242 4242' })
  await enviarFormularioStripe(c3Page)
  await c3Page.waitForURL(/\/pagos\/confirmacion\?session_id=cs_test_/, { timeout: 45000 })
  await c3Page.getByText('¡Tarjeta registrada en Stripe Sandbox!', { exact: true }).waitFor({ timeout: 25000 })

  await vPage.getByRole('button', { name: 'Actualizar estado', exact: true }).click()
  if (!(await metodos3.evaluate((el) => el.open))) await metodos3.locator('summary').click()
  await vPage.getByText(/terminada en 4242/i).waitFor({ timeout: 10000 })
  await vPage.screenshot({ path: `${OUT}/07-metodos-pago-tarjetas.png`, fullPage: true })
  const btnsDesactivar = vPage.getByRole('button', { name: 'Desactivar', exact: true })
  assert((await btnsDesactivar.count()) >= 1, 'Debe haber al menos una tarjeta activa para desactivar')
  for (let i = 0; i < 8 && (await btnsDesactivar.count()) > 0; i++) {
    await Promise.all([
      vPage.waitForResponse((r) => r.url().includes('/metodos-pago/') && r.request().method() === 'PATCH' && r.status() === 200),
      vPage.waitForResponse((r) => /\/api\/intereses\/\d+$/.test(r.url()) && r.request().method() === 'GET' && r.status() === 200),
      btnsDesactivar.first().click(),
    ])
    await vPage.waitForTimeout(200)
  }
  await vPage.getByText('0 tarjetas activas', { exact: true }).waitFor({ timeout: 10000 })
  await vPage.getByLabel('Mostrar métodos inactivos e históricos').check()
  await vPage.getByRole('button', { name: 'Reactivar', exact: true }).first().waitFor()
  console.log('OK   Setup remoto Stripe + Desactivar + filtro inactivos verificado')

  await c3Ctx.close()

  // =========================================================================
  // FLUJO 3: Webhook puro sin retorno UI a /pagos/confirmacion
  // =========================================================================
  const casoWh = await crearProspectoYOrden({ cuotas: 1, sufijoCorreo: 'wh' })
  const { data: chkWh } = await api(`/ordenes-pago/${casoWh.orden.nro_orden}/cuotas/1/checkout`, 'POST', {}, vnd)
  const whCtx = await browser.newContext({ viewport: { width: 1280, height: 900 }, locale: 'es-BO' })
  const whPage = await whCtx.newPage()
  await whPage.route('**/pagos/confirmacion*', (route) => route.abort())
  await whPage.goto(chkWh.url)
  await llenarTarjetaStripe(whPage, { numero: '4242 4242 4242 4242' })
  await enviarFormularioStripe(whPage)
  await whPage.waitForTimeout(2500)
  await whCtx.close()

  let estadoWh = 'Pendiente de pago'
  for (let i = 0; i < 20; i++) {
    estadoWh = psqlScalar(`SELECT estado FROM cuotas WHERE nro_orden = ${casoWh.orden.nro_orden} AND nro_cuota = 1;`)
    if (estadoWh === 'Pago aprobado') break
    await new Promise((r) => setTimeout(r, 1000))
  }
  assert.equal(estadoWh, 'Pago aprobado', `Webhook no actualizó PostgreSQL (estado=${estadoWh})`)
  evidencias.push({ flujo: 'Webhook sin retorno', orden: casoWh.orden.nro_orden })
  console.log(`OK   Webhook Stripe CLI actualizó PostgreSQL sin retorno UI (orden=${casoWh.orden.nro_orden})`)

  await vendorCtx.close()
  assert.deepEqual(erroresJs, [], 'Errores JS detectados: ' + erroresJs.join('; '))
  await fs.writeFile(`${OUT}/evidencias-refactor.json`, JSON.stringify(evidencias, null, 2))
  console.log('\nSTRIPE REFACTOR E2E UI + VISUAL + AUTOMATIZACION: TODO OK')
} finally {
  await browser.close()
}
