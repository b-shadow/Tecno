// Capturas y errores de consola de cada página por rol (base local de desarrollo sembrada).
// Uso: node scripts/capturas_p2.mjs [http://localhost:5173] [carpeta]   (el frontend; Vite reenvía /api)
import { createRequire } from 'node:module'
import fs from 'node:fs/promises'
const require = createRequire(new URL('../presentacion/package.json', import.meta.url))
const { chromium } = require('playwright')

const base = process.argv[2] || 'http://localhost:5173'
const out = process.argv[3] || '.impeccable/review/p2'
await fs.mkdir(out, { recursive: true })
const roles = {
  admin: ['admin@crm-educativo.local', 'Admin12345', ['/dashboard', '/embudo', '/agenda', '/validacion-pagos', '/alumnos', '/reportes', '/usuarios', '/matriz-acceso', '/bitacora', '/motivos-perdida', '/interesados', '/prospectos', '/seguimiento', '/notificaciones', '/gestion-anuncios']],
  vendedor: ['vendedor.demo@crm-educativo.local', 'Vendedor12345', ['/inicio-vendedor', '/embudo', '/agenda']],
}
const tamanos = { escritorio: { width: 1440, height: 900 }, celular: { width: 390, height: 844 } }
const errores = []
const browser = await chromium.launch()

for (const [tam, viewport] of Object.entries(tamanos)) {
  const ctx = await browser.newContext({ viewport, deviceScaleFactor: 1 })
  const page = await ctx.newPage()
  if (process.env.TEMA) await page.addInitScript((modo) => localStorage.setItem('crm_apariencia', JSON.stringify({ modo, audiencia: 'adultos', letra: 0, contraste: 'normal' })), process.env.TEMA)
  page.on('pageerror', (e) => errores.push(`${tam} ${page.url()}: ${e.message}`))
  page.on('console', (m) => m.type() === 'error' && errores.push(`${tam} ${page.url()}: ${m.text()}`))
  await page.goto(`${base}/anuncios`)
  await page.waitForLoadState('networkidle')
  await page.screenshot({ path: `${out}/${tam}-catalogo.png`, fullPage: false })
  await page.goto(`${base}/login`)
  await page.waitForLoadState('networkidle')
  await page.screenshot({ path: `${out}/${tam}-login.png` })
  for (const [rol, [correo, clave, paginas]] of Object.entries(roles)) {
    await page.goto(`${base}/login`)
    await page.getByLabel('Correo', { exact: true }).fill(correo)
    await page.locator('input[autocomplete="current-password"]').fill(clave)
    await page.getByRole('button', { name: 'Ingresar', exact: true }).click()
    await page.waitForLoadState('networkidle')
    for (const ruta of (tam === 'celular' ? paginas.slice(0, 4) : paginas)) {
      await page.goto(`${base}${ruta}`)
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(350)
      const desborde = await page.evaluate(() => document.documentElement.scrollWidth - innerWidth)
      if (desborde > 2) errores.push(`${tam} ${rol} ${ruta}: desborde horizontal de ${desborde}px`)
      await page.screenshot({ path: `${out}/${tam}-${rol}${ruta.replaceAll('/', '-')}.png` })
    }
    await page.evaluate(() => { localStorage.clear(); sessionStorage.clear() })
  }
  await ctx.close()
}
await browser.close()
console.log(errores.length ? errores.join('\n') : 'Sin errores de consola ni desbordes.')
