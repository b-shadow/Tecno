/**
 * Pruebas E2E reales sobre navegador Playwright Chromium contra UNEXO + Stripe Checkout Sandbox oficial.
 * Cubre: P01 (pago único Visa), P02 (rechazada), P03 (fondos insuficientes), P04 (cancelación),
 * P05 (plan 3 cuotas), P08 (recarga confirmación), P15 (cuota ya pagada), P16/P17 (Setup tarjeta + activar/desactivar),
 * P18 (3D Secure), P22 (matrícula y comisión), además de capturas oficiales en qa-artifacts/fase-b/.
 */
import { createRequire } from 'node:module'
import assert from 'node:assert/strict'
import fs from 'node:fs/promises'

const require = createRequire(new URL('../presentacion/package.json', import.meta.url))
const { chromium } = require('playwright')

const BASE = (process.env.QA_BASE || 'http://localhost:5173').replace(/\/$/, '')
const API = (process.env.QA_API || 'http://127.0.0.1:8001/api').replace(/\/$/, '')
const OUT = 'qa-artifacts/fase-b'
await fs.mkdir(OUT, { recursive: true })

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
const mod = cat.programas[0].modulos[0]

async function crearProspectoYOrden({ cuotas, primerVencimiento = '2030-07-01' }) {
  const uid = String(Date.now()).slice(-7)
  const doc = `E2E${uid}`
  const { status: stP, data: dP } = await api('/prospectos', 'POST', {
    documento: doc, nombre: 'Valeria', apellido: 'Stripe Prueba',
    correo: `valeria.${uid}@example.invalid`, telefono: '71234567',
    profesion: 'Ingeniera Comercial', ubicacion: 'Santa Cruz', origen: 'Web',
    modulo_codigo: mod.codigo,
  }, adm)
  assert.equal(stP, 201, JSON.stringify(dP))
  const nroTarjeta = dP.prospecto.intereses[0].nro_tarjeta
  const { status: stA } = await api(`/intereses/${nroTarjeta}/asignar`, 'PATCH', { vendedor_correo: 'vendedor.demo@crm-educativo.local' }, adm)
  assert.equal(stA, 200)
  const { status: stO, data: dO } = await api(`/intereses/${nroTarjeta}/ordenes-pago`, 'POST', {
    modulos: [mod.codigo], cuotas, primer_vencimiento: primerVencimiento,
  }, vnd)
  assert.equal(stO, 201, JSON.stringify(dO))
  return { doc, nroTarjeta, orden: dO.orden }
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

async function llenarTarjetaStripe(page, { numero, vencimiento = '1230', cvc = '123', titular = 'Valeria Stripe Prueba' }) {
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
  let capturado = false
  while (Date.now() < deadline) {
    if (page.url().includes('/pagos/confirmacion')) return
    for (const frame of page.frames()) {
      if (!frame.url().includes('3d_secure_2_test')) continue
      const btn = frame.locator('#test-source-authorize-3ds').first()
      if (await btn.isVisible().catch(() => false)) {
        await page.waitForTimeout(1600)
        if (!capturado) {
          await page.screenshot({ path: `${OUT}/06b-stripe-3ds.png` }).catch(() => {})
          capturado = true
        }
        await btn.click({ force: true }).catch(() => {})
        await page.waitForTimeout(1500)
        if (page.url().includes('/pagos/confirmacion')) return
      }
    }
    await page.waitForTimeout(400)
  }
  throw new Error('No se completó el desafío 3DS de prueba en Stripe Checkout')
}

const browser = await chromium.launch({ headless: true })
const evidencias = []
try {
  const context = await browser.newContext({ viewport: { width: 1280, height: 900 }, locale: 'es-BO', timezoneId: 'America/La_Paz' })
  const page = await context.newPage()
  const erroresJs = []
  page.on('pageerror', (e) => erroresJs.push(e.message))

  // Login en UNEXO como vendedor
  await page.goto(`${BASE}/login`)
  await page.getByLabel('Correo', { exact: true }).fill('vendedor.demo@crm-educativo.local')
  await page.locator('input[autocomplete="current-password"]').fill('Vendedor12345')
  await page.getByRole('button', { name: 'Ingresar', exact: true }).click()
  await page.waitForURL(/inicio-vendedor/)

  // =========================================================================
  // P01 + P08 + P15 + P22: Pago único exitoso Visa 4242 + recarga + matrícula
  // =========================================================================
  const caso1 = await crearProspectoYOrden({ cuotas: 1 })
  await page.goto(`${BASE}/agenda?interes=${caso1.nroTarjeta}`)
  await page.getByRole('tab', { name: 'Pagos', exact: true }).click()
  await page.getByRole('button', { name: 'Pagar con Stripe', exact: true }).waitFor()
  await page.getByRole('button', { name: 'Pagar con Stripe', exact: true }).scrollIntoViewIfNeeded()
  await page.waitForTimeout(200)
  await page.screenshot({ path: `${OUT}/01-modulo-pagos-y-boton-stripe.png` })

  await page.getByRole('button', { name: 'Pagar con Stripe', exact: true }).click()
  await llenarTarjetaStripe(page, { numero: '4242 4242 4242 4242' })
  await page.waitForTimeout(600)
  await page.screenshot({ path: `${OUT}/02-stripe-checkout-bob.png` })
  const textoCheckout = await page.locator('body').innerText()
  assert(/BOB|Bs/i.test(textoCheckout), 'Checkout debe mostrar moneda BOB')

  await enviarFormularioStripe(page)
  await page.waitForURL(/\/pagos\/confirmacion\?session_id=cs_test_/, { timeout: 45000 })
  await page.getByText('¡Pago confirmado por Stripe Sandbox!', { exact: true }).waitFor({ timeout: 25000 })
  await page.screenshot({ path: `${OUT}/03-unexo-confirmacion-exito.png`, fullPage: true })

  const sesion1 = new URL(page.url()).searchParams.get('session_id')
  const { data: ver1 } = await api(`/pagos/stripe/sesiones/${sesion1}`, 'GET', null, vnd)
  assert.equal(ver1.estado_interno, 'confirmado')
  assert.equal(ver1.moneda, 'BOB')
  assert.equal(ver1.saldo_pendiente, 0)
  assert.equal(ver1.estado_comercial, 'Convertido')
  assert(ver1.stripe_pago_intent?.startsWith('pi_'), 'Falta PaymentIntent real')
  evidencias.push({ prueba: 'P01 (Pago único Visa)', orden: caso1.orden.nro_orden, cuota: 1, monto: ver1.monto, cs: ver1.stripe_sesion, pi: ver1.stripe_pago_intent, estado: ver1.estado_interno })
  console.log(`OK   P01 pago único Visa confirmado: orden=${caso1.orden.nro_orden} cs=${ver1.stripe_sesion} pi=${ver1.stripe_pago_intent}`)

  // P08: recargar pantalla de confirmación y validar Footer + responsividad 390px
  await page.reload({ waitUntil: 'networkidle' })
  await page.getByText('¡Pago confirmado por Stripe Sandbox!', { exact: true }).waitFor({ timeout: 15000 })
  await page.setViewportSize({ width: 390, height: 844 })
  await page.waitForTimeout(200)
  const ovConfirm = await page.evaluate(() => document.documentElement.scrollWidth > window.innerWidth + 2)
  assert(!ovConfirm, 'Desbordamiento horizontal en /pagos/confirmacion a 390px')
  assert(await page.locator('footer').textContent().then((t) => /visitas a esta página/i.test(t || '')), 'Falta contador de visitas en footer')
  await page.setViewportSize({ width: 1280, height: 900 })
  console.log('OK   P08 recarga de confirmación idempotente + responsivo 390px + footer con contador')

  // P15: cuota ya pagada rechaza nuevo checkout
  const { status: stP15 } = await api(`/ordenes-pago/${caso1.orden.nro_orden}/cuotas/1/checkout`, 'POST', {}, vnd)
  assert.equal(stP15, 422)
  console.log('OK   P15 intento de segundo pago sobre cuota liquidada bloqueado (422)')

  // =========================================================================
  // P02 (rechazo) + P03 (fondos insuficientes) + P04 (cancelación) + P05 (3 cuotas) + P18 (3DS)
  // =========================================================================
  const caso3 = await crearProspectoYOrden({ cuotas: 3 })
  await page.goto(`${BASE}/agenda?interes=${caso3.nroTarjeta}`)
  await page.getByRole('tab', { name: 'Pagos', exact: true }).click()
  await page.getByRole('button', { name: 'Pagar con Stripe', exact: true }).first().click()

  // P02: tarjeta rechazada 4000 0000 0000 0002
  const frameErr = await llenarTarjetaStripe(page, { numero: '4000 0000 0000 0002' })
  await enviarFormularioStripe(page)
  await frameErr.locator('button[data-testid="payment-form-submit-button"]:not([disabled])').waitFor({ timeout: 25000 })
  await frameErr.locator('[role="alert"], .p-FieldError, :text-matches("rechazada|declined", "i")').first().waitFor({ timeout: 10000 })
  await page.screenshot({ path: `${OUT}/04-stripe-pago-rechazado.png` })
  console.log('OK   P02 tarjeta rechazada bloqueada por Stripe Checkout')

  // P03: fondos insuficientes 4000 0000 0000 9995
  await llenarTarjetaStripe(page, { numero: '4000 0000 0000 9995' })
  await enviarFormularioStripe(page)
  await frameErr.locator('button[data-testid="payment-form-submit-button"]:not([disabled])').waitFor({ timeout: 25000 })
  await frameErr.locator('[role="alert"], :text-matches("fondos|insufficient|rechazada|declined", "i")').first().waitFor({ timeout: 10000 })
  await page.screenshot({ path: `${OUT}/05-stripe-fondos-insuficientes.png` })
  console.log('OK   P03 fondos insuficientes rechazados por Stripe Checkout')

  // Confirmar que BD sigue pendiente sin cobros antes de cancelar
  const { data: intAntes } = await api(`/intereses/${caso3.nroTarjeta}`, 'GET', null, vnd)
  assert.equal(intAntes.interes.ordenes_pago[0].cuotas[0].estado, 'Pendiente de pago')

  // P04: cancelar / volver desde Stripe Checkout hacia /pagos/cancelado
  const urlCancel = await page.evaluate(() => {
    const a = [...document.querySelectorAll('a')].find((el) => (el.href || '').includes('cancelado') || el.getAttribute('aria-label')?.match(/back|volver|atrás/i))
    return a?.href || null
  })
  if (urlCancel) {
    await page.goto(urlCancel)
  } else {
    const backBtn = page.locator('header a, [data-testid="business-link"], a[aria-label]').first()
    await backBtn.click()
  }
  await page.waitForURL(/\/pagos\/cancelado/, { timeout: 25000 })
  await page.getByRole('button', { name: 'Intentar nuevamente' }).waitFor({ timeout: 20000 })
  await page.screenshot({ path: `${OUT}/06-unexo-pago-cancelado.png` })
  console.log('OK   P04 pantalla de cancelación verificada con estado real y botón Intentar nuevamente')

  // P05 Cuota 1 + P18 (3DS 4000 0025 0000 3155) desde botón "Intentar nuevamente"
  await page.getByRole('button', { name: 'Intentar nuevamente' }).click()
  await llenarTarjetaStripe(page, { numero: '4000 0025 0000 3155' })
  await enviarFormularioStripe(page)
  await aprobar3DS(page)
  await page.waitForURL(/\/pagos\/confirmacion\?session_id=cs_test_/, { timeout: 45000 })
  await page.getByText('¡Pago confirmado por Stripe Sandbox!', { exact: true }).waitFor({ timeout: 25000 })
  const sesC1 = new URL(page.url()).searchParams.get('session_id')
  const { data: dC1 } = await api(`/pagos/stripe/sesiones/${sesC1}`, 'GET', null, vnd)
  assert(dC1.saldo_pendiente > 0, 'Plan 3 cuotas tras cuota 1 debe mantener saldo pendiente')
  evidencias.push({ prueba: 'P05+P18 (Cuota 1/3 · 3DS)', orden: caso3.orden.nro_orden, cuota: 1, monto: dC1.monto, cs: dC1.stripe_sesion, pi: dC1.stripe_pago_intent, estado: dC1.estado_interno })
  console.log(`OK   P18/P05 cuota 1/3 (3DS) confirmada: saldo=${dC1.saldo_pendiente} BOB pi=${dC1.stripe_pago_intent}`)

  // Captura en Agenda con 1 de 3 cuotas pagadas y saldo actualizado
  await page.getByRole('button', { name: 'Ver orden en Agenda' }).click()
  await page.getByRole('tab', { name: 'Pagos', exact: true }).click()
  await page.getByText(/1 de 3 cuotas/).waitFor()
  await page.screenshot({ path: `${OUT}/07-plan-3-cuotas-saldo-parcial.png`, fullPage: true })

  // P05 Cuota 2 (Mastercard 5555 5555 5555 4444)
  await page.getByRole('button', { name: 'Pagar con Stripe', exact: true }).first().click()
  await llenarTarjetaStripe(page, { numero: '5555 5555 5555 4444' })
  await enviarFormularioStripe(page)
  await page.waitForURL(/\/pagos\/confirmacion\?session_id=cs_test_/, { timeout: 45000 })
  await page.getByText('¡Pago confirmado por Stripe Sandbox!', { exact: true }).waitFor({ timeout: 25000 })
  const sesC2 = new URL(page.url()).searchParams.get('session_id')
  const { data: dC2 } = await api(`/pagos/stripe/sesiones/${sesC2}`, 'GET', null, vnd)
  evidencias.push({ prueba: 'P05 (Cuota 2/3 · Mastercard)', orden: caso3.orden.nro_orden, cuota: 2, monto: dC2.monto, cs: dC2.stripe_sesion, pi: dC2.stripe_pago_intent, estado: dC2.estado_interno })
  console.log(`OK   P05 cuota 2/3 (Mastercard) confirmada: saldo=${dC2.saldo_pendiente} BOB pi=${dC2.stripe_pago_intent}`)

  // P05 Cuota 3 (Visa 4242 -> liquidación completa saldo 0 Bs)
  await page.getByRole('button', { name: 'Ver orden en Agenda' }).click()
  await page.getByRole('tab', { name: 'Pagos', exact: true }).click()
  await page.getByRole('button', { name: 'Pagar con Stripe', exact: true }).first().click()
  await llenarTarjetaStripe(page, { numero: '4242 4242 4242 4242' })
  await enviarFormularioStripe(page)
  await page.waitForURL(/\/pagos\/confirmacion\?session_id=cs_test_/, { timeout: 45000 })
  await page.getByText('¡Pago confirmado por Stripe Sandbox!', { exact: true }).waitFor({ timeout: 25000 })
  const sesC3 = new URL(page.url()).searchParams.get('session_id')
  const { data: dC3 } = await api(`/pagos/stripe/sesiones/${sesC3}`, 'GET', null, vnd)
  assert.equal(dC3.saldo_pendiente, 0, 'Tras 3ra cuota el saldo debe ser 0')
  evidencias.push({ prueba: 'P05 (Cuota 3/3 · Liquidación)', orden: caso3.orden.nro_orden, cuota: 3, monto: dC3.monto, cs: dC3.stripe_sesion, pi: dC3.stripe_pago_intent, estado: dC3.estado_interno })
  console.log(`OK   P05 cuota 3/3 confirmada -> saldo=${dC3.saldo_pendiente} BOB pi=${dC3.stripe_pago_intent}`)

  await page.getByRole('button', { name: 'Ver orden en Agenda' }).click()
  await page.getByRole('tab', { name: 'Pagos', exact: true }).click()
  await page.getByText(/3 de 3 cuotas/).waitFor()
  await page.screenshot({ path: `${OUT}/08-plan-3-cuotas-liquidado.png`, fullPage: true })

  // =========================================================================
  // P16 + P17: Registro oficial de tarjeta (Stripe Setup) + activar/desactivar
  // =========================================================================
  await page.getByRole('button', { name: 'Registrar tarjeta con Stripe', exact: true }).click()
  await llenarTarjetaStripe(page, { numero: '4242 4242 4242 4242' })
  await enviarFormularioStripe(page)
  await page.waitForURL(/\/pagos\/confirmacion\?session_id=cs_test_/, { timeout: 45000 })
  await page.getByText('¡Tarjeta registrada en Stripe Sandbox!', { exact: true }).waitFor({ timeout: 25000 })
  await page.screenshot({ path: `${OUT}/09-stripe-setup-confirmado.png` })
  const sesSetup = new URL(page.url()).searchParams.get('session_id')
  const { data: dSetup } = await api(`/pagos/stripe/sesiones/${sesSetup}`, 'GET', null, vnd)
  assert(dSetup.stripe_cliente?.startsWith('cus_') && dSetup.stripe_metodo?.startsWith('pm_'))
  evidencias.push({ prueba: 'P16 (Setup Tarjeta)', orden: '-', cuota: '-', monto: 0, cs: dSetup.stripe_sesion, pi: dSetup.stripe_metodo, estado: dSetup.estado_interno })
  console.log(`OK   P16 método guardado vía Stripe Setup: customer=${dSetup.stripe_cliente} pm=${dSetup.stripe_metodo}`)

  await page.getByRole('button', { name: 'Ver orden en Agenda' }).click()
  await page.getByRole('tab', { name: 'Pagos', exact: true }).click()
  await page.getByText(/Stripe Sandbox/).first().waitFor()
  await page.getByRole('button', { name: 'Desactivar', exact: true }).first().click()
  await page.getByText('Método desactivado.', { exact: true }).waitFor()
  await page.getByRole('button', { name: 'Activar', exact: true }).first().click()
  await page.getByText('Método activado.', { exact: true }).waitFor()
  await page.screenshot({ path: `${OUT}/10-metodos-pago-stripe.png` })
  console.log('OK   P17 método Stripe desactivado y reactivado en Agenda')

  assert.deepEqual(erroresJs, [], 'Errores JS detectados: ' + erroresJs.join('; '))
  await fs.writeFile(`${OUT}/transacciones-reales.json`, JSON.stringify(evidencias, null, 2))
  console.log('\nSTRIPE E2E UI: TODO OK')
} finally {
  await browser.close()
}
