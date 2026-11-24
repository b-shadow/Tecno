// Pruebas contra QA desechable, con navegadores aislados de las ventanas del usuario.
import { createRequire } from 'node:module'
import fs from 'node:fs/promises'
import assert from 'node:assert/strict'
const require = createRequire(new URL('../presentacion/package.json', import.meta.url))
const { chromium, firefox, webkit } = require('playwright')
const base = process.env.QA_BASE || 'http://localhost:18002'
assert(['localhost', '127.0.0.1', 'crm-qa-audit'].includes(new URL(base).hostname), 'Solo QA aislado')
const out = 'qa-artifacts'
await fs.mkdir(out, { recursive: true })
const results = []
const sizes = [[320,740],[390,844],[768,1024],[1280,900]]
const common = ['/embudo','/prospectos','/agenda','/seguimiento','/reportes','/notificaciones']
const roles = [
  { id:'admin', correo:'admin@crm-educativo.local', password:'Admin12345', home:'/dashboard', pages:['/dashboard','/usuarios','/matriz-acceso','/bitacora','/motivos-perdida','/gestion-anuncios','/interesados','/validacion-pagos','/alumnos',...common] },
  { id:'coordinador', correo:'coord@test.local', password:'Clave12345', home:'/dashboard', pages:['/dashboard','/motivos-perdida','/gestion-anuncios','/interesados','/validacion-pagos','/alumnos',...common] },
  { id:'vendedor', correo:'vendedor.demo@crm-educativo.local', password:'Vendedor12345', home:'/inicio-vendedor', pages:['/inicio-vendedor',...common] },
]

async function settle(page) {
  await page.waitForLoadState('networkidle')
  await page.locator('main').waitFor()
}
// Botón de la cuenta: el último botón desplegable del encabezado (después de Apariencia).
const perfil=(page)=>page.locator('header').getByRole('button',{expanded:false}).last()

async function login(page, role, remember=true) {
  await page.goto(base+'/login')
  await page.getByLabel('Correo',{exact:true}).fill(role.correo)
  await page.locator('input[autocomplete="current-password"]').fill(role.password)
  await page.getByRole('checkbox',{name:'Recordarme'}).setChecked(remember)
  await page.getByRole('button',{name:'Ingresar',exact:true}).click()
  await page.waitForURL(base+role.home)
  await settle(page)
}
async function layout(page) {
  const dimensions = await page.evaluate(() => {
    const main = document.querySelector('main')
    return { window:innerWidth, doc:document.documentElement.scrollWidth, main:main.clientWidth, content:main.scrollWidth,
      broken:[...document.images].filter(i => i.complete && !i.naturalWidth && getComputedStyle(i).display!=='none').map(i=>i.getAttribute('src')) }
  })
  assert(dimensions.doc <= dimensions.window+2, 'Desbordamiento del documento: '+JSON.stringify(dimensions))
  assert(dimensions.content <= dimensions.main+2, 'Desbordamiento de la pagina: '+JSON.stringify(dimensions))
  assert.equal(dimensions.broken.length,0,'Imagenes sin cargar: '+dimensions.broken.join(','))
  const visibleErrors = await page.locator('.error-message:visible').allTextContents()
  assert(!visibleErrors.some(s=>s.trim()),'Error visible: '+visibleErrors.join(' / '))
}
async function shot(page, name) { await page.screenshot({path:`${out}/${name}.png`,animations:'disabled'}) }

async function audit(engine) {
  const browser = await ({chromium,firefox,webkit})[engine].launch({headless:true})
  let page
  const errors=[]
  const contexts=[]
  async function test(name, run) {
    try { await run(); results.push({engine,name,ok:true}) }
    catch(error) {
      results.push({engine,name,ok:false,error:error.message})
      console.error('FAIL',engine,name,error.message)
      if(page) await shot(page,`${engine}-FAIL-${results.length}`).catch(()=>{})
    }
  }
  try {
    const visitor = await browser.newContext({viewport:{width:390,height:844},locale:'es-BO',timezoneId:'America/La_Paz'})
    contexts.push(visitor)
    page=await visitor.newPage()
    page.on('pageerror',e=>errors.push(e.message))
    await test('catalogo y registro publico movil',async()=>{
      await page.goto(base+'/anuncios'); await settle(page)
      await layout(page)
      await page.locator('tbody th button').first().click()
      await page.getByRole('button',{name:'Me interesa el programa',exact:true}).click()
      const unique=engine+'-'+Date.now()
      const ci=String(Date.now()).slice(-9)
      await page.getByLabel('Nombre *',{exact:true}).fill('Visual')
      await page.getByLabel('Apellido *',{exact:true}).fill('Prueba Visual')
      await page.getByPlaceholder('Nro. de documento').fill('QA'+ci)
      await page.getByPlaceholder('Ej. 71234567').fill('00007777')
      await page.getByPlaceholder('Ej. Ingeniero de sistemas').fill('QA')
      await page.getByPlaceholder('Ej. Santa Cruz').fill('Entorno aislado')
      await page.getByPlaceholder('usted@correo.com').fill(unique+'@example.invalid')
      const button=page.getByRole('button',{name:'Enviar interés',exact:true})
      const rect=await button.boundingBox()
      assert(rect.x+rect.width<390,'Boton de registro recortado')
      await button.click()
      await page.getByText('Interés registrado correctamente.',{exact:false}).waitFor()
      await shot(page,engine+'-publico-registro')
      await page.locator('main').evaluate(e=>e.scrollTop=e.scrollHeight)
      await page.getByRole('link',{name:'Iniciar sesión',exact:true}).click()
      await page.waitForURL(base+'/login')
      await settle(page)
      assert(await page.evaluate(()=>scrollY)<2,'Navegacion conserva desplazamiento anterior')
      await page.getByRole('button',{name:'¿Olvidó su contraseña?',exact:true}).click()
      await page.getByText('Solicite al administrador que restablezca su contraseña desde Usuarios.',{exact:true}).waitFor()
    })

    for(const role of roles) {
      const context=await browser.newContext({viewport:{width:1280,height:900},locale:'es-BO',timezoneId:'America/La_Paz'})
      contexts.push(context)
      page=await context.newPage()
      const resourceErrors=[]
      page.on('pageerror',e=>errors.push(e.message))
      page.on('response',r=>{if(r.status()>=500)resourceErrors.push(r.status()+' '+new URL(r.url()).pathname)})
      page.on('requestfailed',r=>{if(!r.failure()?.errorText?.includes('ABORTED')&&!r.failure()?.errorText?.includes('cancelled'))resourceErrors.push(r.url())})
      let loggedIn=false
      await test(role.id+' login sin recordar',async()=>{
        await login(page,role,false); loggedIn=true
        const stored=await page.evaluate(()=>({local:!!localStorage.getItem('crm_token'),session:!!sessionStorage.getItem('crm_token')}))
        assert.deepEqual(stored,{local:false,session:true})
        await page.reload(); await settle(page)
        assert.equal(new URL(page.url()).pathname,role.home)
      })
      if(!loggedIn)continue
      for(const path of role.pages) {
        await test(role.id+' '+path,async()=>{
          await page.goto(base+path); await settle(page)
          assert.equal(new URL(page.url()).pathname,path,'Redireccion inesperada')
          for(const [width,height] of sizes) {
            await page.setViewportSize({width,height})
            for(const theme of ['light','dark']) {
              const current=await page.locator('html').getAttribute('data-theme')
              if(current!==theme) await page.getByRole('button',{name:theme==='dark'?'Modo oscuro':'Modo claro',exact:true}).click()
              await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))))
              await layout(page)
              if(width===390||width===1280)await shot(page,`${engine}-${role.id}-${path.slice(1)}-${width}-${theme}`)
              results.push({engine,name:`vista ${role.id} ${path} ${width} ${theme}`,ok:true})
            }
          }
        })
      }
      await test(role.id+' perfil adaptable y agenda movil',async()=>{
        await page.setViewportSize({width:390,height:844})
        await perfil(page).click()
        await page.getByRole('button',{name:'Mi perfil',exact:true}).click()
        const card=page.getByRole('dialog',{name:'Mi perfil'})
        await card.waitFor()
        for(const width of [320,390,1280]) {
          await page.setViewportSize({width,height:844})
          const bounds=await card.boundingBox()
          assert(bounds.x>=0 && bounds.x+bounds.width<=width+1,'Perfil recortado')
          assert(await card.evaluate(e=>e.scrollWidth<=e.clientWidth+2),'Perfil con desbordamiento horizontal')
          await card.locator('input').last().scrollIntoViewIfNeeded()
          await shot(page,`${engine}-${role.id}-perfil-${width}`)
        }
        await card.getByRole('button',{name:'Cerrar',exact:true}).first().click()
        await page.setViewportSize({width:390,height:844})
        await page.goto(base+'/agenda'); await settle(page)
        if(await page.locator('.chat-list-item').count()) {
          await page.locator('.chat-list-item').first().click()
          await page.locator('.agenda-detail-window').waitFor()
          await page.waitForFunction(()=> {
            const top=document.querySelector('.agenda-detail-window').getBoundingClientRect().top
            return top>=-2 && top<140
          })
          await layout(page)
          await shot(page,`${engine}-${role.id}-agenda-detalle-movil`)
          await page.getByRole('button',{name:'Volver a los interesados',exact:true}).click()
          await page.locator('.chat-list-item').first().waitFor()
          await page.waitForFunction(()=>document.querySelector('.chat-list-item').getBoundingClientRect().top<innerHeight)
        }
      })
      await test(role.id+' errores de ejecucion y servidor',async()=>{
        assert.deepEqual(resourceErrors,[], 'Peticiones fallidas o errores 500')
        assert.deepEqual(errors,[], 'Errores JavaScript')
      })
      if(role.id==='admin') {
        await test('proteccion del ultimo administrador en la interfaz',async()=>{
          await page.goto(base+'/usuarios'); await settle(page)
          const row=page.locator('tr').filter({hasText:'admin@crm-educativo.local'})
          await row.getByRole('button',{name:'Desactivar',exact:true}).click()
          await page.getByText('Debe conservar al menos un administrador activo.',{exact:true}).waitFor()
          await row.getByText('activo',{exact:true}).waitFor()
        })
      }
      if(role.id==='vendedor') {
        await test('vendedor no abre usuarios ni pagos',async()=>{
          for(const path of ['/usuarios','/validacion-pagos','/interesados','/alumnos']) {
            await page.goto(base+path); await page.waitForURL(base+role.home); await settle(page)
          }
        })
      }
      await test(role.id+' cierre de sesion',async()=>{
        await perfil(page).click()
        await page.getByRole('button',{name:'Cerrar sesión',exact:true}).click()
        await page.getByRole('dialog',{name:'¿Cerrar sesión?'}).getByRole('button',{name:'Cerrar sesión',exact:true}).click()
        await page.waitForURL(base+'/login'); await settle(page)
        assert.equal(await page.evaluate(()=>!!(localStorage.getItem('crm_token')||sessionStorage.getItem('crm_token'))),false)
      })
      console.log('OK matriz',engine,role.id,role.pages.length+' paginas, cuatro anchos y dos temas')
    }
  } finally {
    for(const context of contexts)await context.close().catch(()=>{})
    await browser.close()
  }
}

const engines=(process.env.QA_ENGINES||'chromium,firefox,webkit').split(',')
await Promise.all(engines.map(engine=>audit(engine).catch(error=>{
  results.push({engine,name:'inicio del navegador',ok:false,error:error.message})
  console.error('FAIL',engine,error.message)
})))
const failures=results.filter(r=>!r.ok)
await fs.writeFile(out+'/summary.json',JSON.stringify({engines,total:results.length,passed:results.length-failures.length,failures,results},null,2))
console.log('NAVEGADORES:',results.length,'comprobaciones;',failures.length,'fallas')
if(failures.length)process.exitCode=1
